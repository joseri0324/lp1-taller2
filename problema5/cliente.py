#!/usr/bin/env python3
"""
Cliente interactivo para probar LIST / UPLOAD / DOWNLOAD / QUIT
"""

import socket
import hashlib
import os

HOST = "localhost"
PORT = 9200
BUFFER = 4096


# -------------------- FUNCIONES AUXILIARES --------------------

def sha256_of_file(path):
    """Calcula el hash SHA-256 de un archivo local."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(BUFFER), b""):
            h.update(chunk)
    return h.hexdigest()


def recv_line(conn):
    """Recibe una línea terminada en \r\n y la devuelve como string."""
    data = b""
    while True:
        ch = conn.recv(1)
        if not ch:
            raise ConnectionError("Conexión cerrada")
        data += ch
        if data.endswith(b"\r\n"):
            return data[:-2].decode("utf-8", errors="replace")


def read_exact(conn, size, out_path=None):
    """Lee exactamente 'size' bytes del servidor y opcionalmente los guarda en un archivo."""
    remaining = size
    if out_path:
        with open(out_path, "wb") as f:
            while remaining > 0:
                chunk = conn.recv(min(BUFFER, remaining))
                if not chunk:
                    raise ConnectionError("Conexión cerrada durante descarga")
                f.write(chunk)
                remaining -= len(chunk)
    else:
        data = b""
        while remaining > 0:
            chunk = conn.recv(min(BUFFER, remaining))
            if not chunk:
                raise ConnectionError("Conexión cerrada durante lectura")
            data += chunk
            remaining -= len(chunk)
        return data


# -------------------- COMANDOS --------------------

def do_list(conn):
    """Pide la lista de archivos al servidor."""
    conn.sendall(b"LIST\r\n")
    line = recv_line(conn)
    print("Servidor:", line)

    # El servidor indica cuántos archivos hay
    if line.startswith("OK"):
        try:
            _, count, _ = line.split(" ", 2)
            n = int(count)
        except:
            n = 0
        for _ in range(n):
            fname = recv_line(conn)
            print(" -", fname)


def do_upload(conn, local_path, remote_name=None):
    """Sube un archivo al servidor."""
    if not os.path.exists(local_path):
        print("Archivo local no existe")
        return

    if not remote_name:
        remote_name = os.path.basename(local_path)

    size = os.path.getsize(local_path)
    sha = sha256_of_file(local_path)

    # Enviar encabezado
    header = f"UPLOAD {remote_name} {size} {sha}\r\n"
    conn.sendall(header.encode())

    # Esperar confirmación
    line = recv_line(conn)
    if not line.startswith("OK"):
        print("Servidor:", line)
        return

    # Enviar el archivo en chunks
    with open(local_path, "rb") as f:
        while chunk := f.read(BUFFER):
            conn.sendall(chunk)

    # Leer confirmación final
    final = recv_line(conn)
    print("Servidor:", final)


def do_download(conn, remote_name, local_path=None):
    """Descarga un archivo del servidor."""
    if not local_path:
        local_path = remote_name

    header = f"DOWNLOAD {remote_name}\r\n"
    conn.sendall(header.encode())

    line = recv_line(conn)
    if not line.startswith("OK"):
        print("Servidor:", line)
        return

    size_line = recv_line(conn)
    _, size_s = size_line.split(" ", 1)
    size = int(size_s)

    read_exact(conn, size, out_path=local_path)
    print(f"Descargado en {local_path} ({size} bytes)")


# -------------------- CLIENTE INTERACTIVO --------------------

def interactive():
    """Loop interactivo del cliente."""
    print(f"Conectando a {HOST}:{PORT} ...")
    conn = socket.create_connection((HOST, PORT))
    try:
        while True:
            cmd = input("> ").strip()
            if not cmd:
                continue
            parts = cmd.split()
            c = parts[0].upper()

            if c == "QUIT":
                conn.sendall(b"QUIT\r\n")
                print(recv_line(conn))
                break
            elif c == "LIST":
                do_list(conn)
            elif c == "UPLOAD":
                if len(parts) < 2:
                    print("Uso: UPLOAD <local_path> [remote_name]")
                else:
                    do_upload(conn, parts[1], parts[2] if len(parts) > 2 else None)
            elif c == "DOWNLOAD":
                if len(parts) < 2:
                    print("Uso: DOWNLOAD <remote_name> [local_path]")
                else:
                    do_download(conn, parts[1], parts[2] if len(parts) > 2 else None)
            else:
                print("Comandos: LIST, UPLOAD, DOWNLOAD, QUIT")
    except KeyboardInterrupt:
        print("Saliendo...")
    finally:
        conn.close()


if __name__ == "__main__":
    interactive()