#!/usr/bin/env python3
"""
Load Balancer simple (round-robin) con health checks.
- Escucha peticiones HTTP simples desde clientes (GET/PUT /key)
- Redirige la petición al backend elegido por round-robin
- Mantiene lista de backends saludables y excluye los caídos
"""

import socket
import threading
import time
import http.client
from urllib.parse import urlparse

HOST = 'localhost'
PORT = 9500        # puerto público del balanceador
HEALTH_INTERVAL = 5      # segundos entre health checks
BACKENDS = [('localhost', 9501), ('localhost', 9502)]  # lista inicial de backends

lock = threading.Lock()
healthy = {}   # (host,port) -> True/False
rr_index = 0    # indice para round-robin

# Inicializar healthy con False
for b in BACKENDS:
    healthy[b] = False

def health_check_worker():
    """Thread que periódicamente verifica /health en cada backend."""
    while True:
        for host, port in BACKENDS:
            ok = False
            try:
                conn = http.client.HTTPConnection(host, port, timeout=2)
                conn.request("GET", "/health")
                resp = conn.getresponse()
                if resp.status == 200:
                    ok = True
                conn.close()
            except Exception:
                ok = False
            with lock:
                healthy[(host, port)] = ok
        time.sleep(HEALTH_INTERVAL)

def choose_backend():
    """Elige un backend healthy por round-robin; devuelve (host,port) o None."""
    with lock:
        available = [b for b, ok in healthy.items() if ok]
        if not available:
            return None
        global rr_index
        backend = available[rr_index % len(available)]
        rr_index += 1
        return backend

def forward_http(client_conn, client_addr, request_data):
    """
    Parsea una petición HTTP mínima y la reenvía al backend elegido.
    request_data: bytes de la petición completa recibida desde cliente.
    """
    backend = choose_backend()
    if backend is None:
        # responder 503 Service Unavailable
        client_conn.sendall(b"HTTP/1.1 503 Service Unavailable\r\nContent-Length: 19\r\n\r\nNo backends alive\n")
        client_conn.close()
        return

    host, port = backend
    try:
        # Conectar al backend
        backend_sock = socket.create_connection((host, port), timeout=5)
        backend_sock.sendall(request_data)  # reenviamos la petición completa
        # Reenviamos la respuesta del backend al cliente (streaming)
        while True:
            chunk = backend_sock.recv(4096)
            if not chunk:
                break
            client_conn.sendall(chunk)
        backend_sock.close()
    except Exception as e:
        # Marca backend como down y responde error al cliente
        with lock:
            healthy[(host, port)] = False
        client_conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 11\r\n\r\nBad Gateway\n")
    finally:
        client_conn.close()

def handle_client(conn, addr):
    """Recibe de cliente, lee petición (hasta doble CRLF) y la reenvía."""
    try:
        # leer petición simple hasta encontrar \r\n\r\n (headers end)
        data = b""
        conn.settimeout(3)
        while b"\r\n\r\n" not in data:
            part = conn.recv(4096)
            if not part:
                break
            data += part
        if not data:
            conn.close()
            return
        # Forward a backend en otro thread para no bloquear LB
        threading.Thread(target=forward_http, args=(conn, addr, data), daemon=True).start()
    except Exception:
        conn.close()

def main():
    # lanzar health check
    threading.Thread(target=health_check_worker, daemon=True).start()
    # crear socket LB
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(64)
        print(f"[LB] Listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()