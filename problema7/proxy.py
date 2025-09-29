#!/usr/bin/env python3
"""
Proxy HTTP (soporta HTTP y HTTPS).
Intercepta peticiones del cliente y las reenvía al servidor destino.
"""

import socket
import threading

HOST = "localhost"
PORT = 9400
BUFFER = 4096

# ----------------- FUNCIONES AUXILIARES -----------------

def log(msg):
    """Guarda logs en consola y en archivo proxy.log"""
    line = f"[LOG] {msg}"
    print(line)
    with open("proxy.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")

def forward(src, dst):  
    """
    Reenvía datos entre dos sockets (cliente <-> servidor).
    - src: socket origen
    - dst: socket destino
    """
    try:
        while True:
            data = src.recv(BUFFER)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        src.close()
        dst.close()

# ----------------- HILO POR CLIENTE -----------------

def handle_client(conn, addr):
    try:
        # Leer la primera petición HTTP
        request = conn.recv(BUFFER)
        if not request:
            conn.close()
            return

        # Decodificar solo la primera línea (ej: "GET http://example.com/ HTTP/1.1")
        try:
            first_line = request.split(b"\n")[0].decode()
        except:
            conn.close()
            return

        log(f"Cliente {addr} → {first_line}")

        # Caso HTTPS: CONNECT host:puerto
        if first_line.startswith("CONNECT"):
            _, target, _ = first_line.split()
            host, port = target.split(":")
            port = int(port)

            # Conectar al destino
            with socket.create_connection((host, port)) as server_sock:
                conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

                # Crear hilos para transmitir datos en ambas direcciones
                t1 = threading.Thread(target=forward, args=(conn, server_sock))
                t2 = threading.Thread(target=forward, args=(server_sock, conn))
                t1.start()
                t2.start()
                t1.join()
                t2.join()

        else:
            # Caso HTTP normal: GET, POST, etc.
            parts = first_line.split()
            if len(parts) < 2:
                conn.close()
                return

            method, url = parts[0], parts[1]

            # Extraer host de los headers
            headers = request.decode(errors="ignore").split("\r\n")
            host_line = next((h for h in headers if h.lower().startswith("host:")), None)

            if not host_line:
                log("No se encontró header Host.")
                conn.close()
                return

            host = host_line.split(":", 1)[1].strip()
            if ":" in host:
                host, port = host.split(":")
                port = int(port)
            else:
                port = 80  # HTTP por defecto

            # Conectar al servidor destino
            with socket.create_connection((host, port)) as server_sock:
                server_sock.sendall(request)

                # Reenviar respuesta al cliente y loguear
                while True:
                    data = server_sock.recv(BUFFER)
                    if not data:
                        break
                    log(f"Respuesta de {host}:{port} → {data[:100].decode(errors='ignore')}")
                    conn.sendall(data)

    except Exception as e:
        log(f"Error con {addr}: {e}")
    finally:
        conn.close()

# ----------------- MAIN -----------------

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        log(f"Proxy escuchando en {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()