#!/usr/bin/env python3
"""
Servidor para transferencia de archivos (UPLOAD / DOWNLOAD / LIST)
- Maneja varios clientes con threads
- Protocolo basado en líneas terminadas en \r\n
- Soporta LIST, UPLOAD, DOWNLOAD y QUIT
"""

import socket
import threading
import os
import hashlib

# Dirección y puerto donde escucha el servidor
HOST = "localhost"
PORT = 9200

# Carpeta donde se guardarán los archivos
BASE_DIR = os.path.abspath("storage")

# Tamaño de buffer para enviar/recibir datos
BUFFER = 4096

# Límite máximo de archivo (1 GB por defecto)
MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024

# Crear la carpeta de almacenamiento si no existe
os.makedirs(BASE_DIR, exist_ok=True)


# -------------------- FUNCIONES AUXILIARES --------------------

def secure_join(base_dir, filename):
    """
    Función de seguridad:
    - Evita que el cliente intente guardar archivos fuera de BASE_DIR (ataque path traversal).
    """
    if "\x00" in filename or filename.startswith("/") or ".." in filename:
        raise ValueError("Nombre de archivo inválido")

    candidate = os.path.normpath(os.path.join(base_dir, filename))
    if not candidate.startswith(base_dir + os.sep):
        raise ValueError("Ruta fuera del directorio permitido")
    return candidate


def recv_line(conn):
    """
    Recibe datos hasta encontrar '\r\n' y retorna la línea como string.
    """
    data = b""
    while True:
        ch = conn.recv(1)
        if not ch:
            raise ConnectionError("Conexión cerrada leyendo línea")
        data += ch
        if data.endswith(b"\r\n"):
            return data[:-2].decode("utf-8", errors="replace")


def read_exact(conn, size):
    """
    Lee exactamente 'size' bytes del socket.
    """
    remaining = size
    chunks = []
    while remaining > 0:
        chunk = conn.recv(min(BUFFER, remaining))
        if not chunk:
            raise ConnectionError("Conexión cerrada antes de recibir todo el archivo")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


# -------------------- HANDLERS DE COMANDOS --------------------

def handle_list(conn):
    """Responde con la lista de archivos en el servidor."""
    files = [f for f in os.listdir(BASE_DIR) if os.path.isfile(os.path.join(BASE_DIR, f))]
    conn.sendall(f"OK {len(files)} files\r\n".encode())
    for f in files:
        conn.sendall((f + "\r\n").encode())


def handle_upload(conn, parts):
    """
    Maneja la subida de un archivo:
    Cliente envía -> UPLOAD <filename> <size> <sha256>
    Luego, tras "OK", envía los bytes del archivo.
    """
    if len(parts) != 4:
        conn.sendall(b"ERR 400 Formato UPLOAD incorrecto\r\n")
        return

    _, filename, size_s, sha256_hex = parts
    try:
        size = int(size_s)
    except:
        conn.sendall(b"ERR 400 Tamano invalido\r\n")
        return

    if size < 0 or size > MAX_FILE_SIZE:
        conn.sendall(b"ERR 413 Archivo demasiado grande\r\n")
        return

    try:
        dest = secure_join(BASE_DIR, filename)
    except ValueError:
        conn.sendall(b"ERR 400 Nombre de archivo invalido\r\n")
        return

    if os.path.exists(dest):
        conn.sendall(b"ERR 409 El archivo ya existe\r\n")
        return

    # Confirmar que estamos listos para recibir
    conn.sendall(b"OK\r\n")

    # Guardar archivo en .tmp hasta confirmar checksum
    tmp_path = dest + ".tmp"
    hasher = hashlib.sha256()

    try:
        with open(tmp_path, "wb") as f:
            remaining = size
            while remaining > 0:
                chunk = conn.recv(min(BUFFER, remaining))
                if not chunk:
                    raise ConnectionError("Conexión cerrada durante subida")
                f.write(chunk)
                hasher.update(chunk)
                remaining -= len(chunk)
    except Exception as e:
        try:
            os.remove(tmp_path)
        except:
            pass
        conn.sendall(f"ERR 500 {str(e)}\r\n".encode())
        return

    # Validar checksum
    if hasher.hexdigest() != sha256_hex.lower():
        os.remove(tmp_path)
        conn.sendall(b"ERR 422 checksum no coincide\r\n")
        return

    # Confirmar éxito
    os.rename(tmp_path, dest)
    conn.sendall(b"OK Archivo guardado\r\n")
    print(f"[UPLOAD] Guardado {filename} ({size} bytes)")


def handle_download(conn, parts):
    """
    Maneja la descarga de un archivo:
    Cliente envía -> DOWNLOAD <filename>
    Servidor responde con "OK" y luego "SIZE <size>" seguido de los bytes.
    """
    if len(parts) != 2:
        conn.sendall(b"ERR 400 Formato DOWNLOAD incorrecto\r\n")
        return

    _, filename = parts
    try:
        path = secure_join(BASE_DIR, filename)
    except ValueError:
        conn.sendall(b"ERRor 400 Nombre de archivo invalido\r\n")
        return

    if not os.path.exists(path):
        conn.sendall(b"ERR 404 Archivo no encontrado\r\n")
        return

    size = os.path.getsize(path)
    conn.sendall(b"OK\r\n")
    conn.sendall(f"SIZE {size}\r\n".encode())

    # Enviar en chunks
    with open(path, "rb") as f:
        while chunk := f.read(BUFFER):
            conn.sendall(chunk)

    print(f"[DOWNLOAD] Enviado {filename} ({size} bytes)")


# -------------------- GESTIÓN DE CLIENTES --------------------

def client_thread(conn, addr):
    """Maneja las peticiones de un cliente en un hilo separado."""
    print(f"[+] Conexión desde {addr}")
    try:
        while True:
            line = recv_line(conn)
            if not line:
                break
            parts = line.strip().split()
            cmd = parts[0].upper()
            print(f"[{addr}] CMD: {line}")

            if cmd == "LIST":
                handle_list(conn)
            elif cmd == "UPLOAD":
                handle_upload(conn, parts)
            elif cmd == "DOWNLOAD":
                handle_download(conn, parts)
            elif cmd == "QUIT":
                conn.sendall(b"OK Bye\r\n")
                break
            else:
                conn.sendall(b"ERR 400 Comando desconocido\r\n")
    except Exception as e:
        print(f"[!] Error con {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Desconectado {addr}")


def run_server():
    """Arranca el servidor principal."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"Servidor escuchando en {HOST}:{PORT}")

    try:
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Servidor detenido")
    finally:
        srv.close()


if __name__ == "__main__":
    run_server()