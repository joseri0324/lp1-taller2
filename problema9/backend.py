#!/usr/bin/env python3
"""
Backend simple con KV store en memoria + replicación a otros backends.
Uso: iniciar varios backends en puertos distintos.
Ejemplo: python3 backend.py 9601  # inicia backend en puerto 9601
"""

import socket
import threading
import sys
import http.client
from urllib.parse import urlparse

HOST = 'localhost'
PORT = 9500
BUFFER = 4096

# lista de otros backends (se puede pasar por argumentos)
# Para simplificar, pasamos todos los backends por línea de comandos al iniciar cada instancia.
# Ej: instancia en 9601: python3 backend.py 9601 9602  (lista de peers)
def parse_args():
    if len(sys.argv) < 2:
        print("Uso: backend.py <mi_puerto> [peer1_port peer2_port ...]")
        sys.exit(1)
    my_port = int(sys.argv[1])
    peers = []
    for p in sys.argv[2:]:
        peers.append(("localhost", int(p)))
    return my_port, peers

class BackendServer:
    def __init__(self, port, peers):
        self.port = port
        self.peers = peers  # lista de (host,port)
        self.store = {}     # KV store en memoria
        self.lock = threading.Lock()

    def handle_connection(self, conn, addr):
        try:
            data = b""
            conn.settimeout(3)
            while b"\r\n\r\n" not in data:
                part = conn.recv(BUFFER)
                if not part:
                    break
                data += part
            if not data:
                conn.close()
                return
            req_text = data.decode(errors="ignore")
            # parse simple first line
            first_line = req_text.splitlines()[0]
            method, path, _ = first_line.split()
            # routing
            if path == "/health" and method == "GET":
                resp = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
                conn.sendall(resp.encode())
                conn.close()
                return
            # GET /get/<key>
            if method == "GET" and path.startswith("/get/"):
                key = path[len("/get/"):]
                with self.lock:
                    val = self.store.get(key)
                if val is None:
                    body = "NOTFOUND"
                    resp = f"HTTP/1.1 404 Not Found\r\nContent-Length: {len(body)}\r\n\r\n{body}"
                else:
                    resp = f"HTTP/1.1 200 OK\r\nContent-Length: {len(val)}\r\n\r\n{val}"
                conn.sendall(resp.encode())
                conn.close()
                return
            # PUT via POST /put/<key> with body after headers
            if method in ("POST","PUT") and path.startswith("/put/"):
                key = path[len("/put/"):]
                # naive: get body after \r\n\r\n
                parts = req_text.split("\r\n\r\n", 1)
                body = parts[1] if len(parts) > 1 else ""
                # store locally
                with self.lock:
                    self.store[key] = body
                # replicate to peers synchronously (best-effort)
                for host, port in self.peers:
                    try:
                        conn_peer = http.client.HTTPConnection(host, port, timeout=2)
                        conn_peer.request("POST", f"/replicate/{key}", body)
                        r = conn_peer.getresponse()
                        conn_peer.close()
                    except Exception:
                        # ignore peer failure; LB health checks will handle unavailability
                        pass
                resp = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
                conn.sendall(resp.encode())
                conn.close()
                return
            # replication endpoint
            if method == "POST" and path.startswith("/replicate/"):
                key = path[len("/replicate/"):]
                parts = req_text.split("\r\n\r\n", 1)
                body = parts[1] if len(parts) > 1 else ""
                with self.lock:
                    self.store[key] = body
                resp = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
                conn.sendall(resp.encode())
                conn.close()
                return

            # default: 400
            resp = "HTTP/1.1 400 Bad Request\r\nContent-Length: 11\r\n\r\nBad Request"
            conn.sendall(resp.encode())
        except Exception as e:
            # en errores cerramos
            try:
                conn.sendall(b"HTTP/1.1 500 Internal\r\nContent-Length:5\r\n\r\nError")
            except:
                pass
        finally:
            conn.close()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, self.port))
            s.listen(64)
            print(f"[BACKEND {self.port}] Listening; peers: {self.peers}")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_connection, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    my_port, peers = parse_args()
    srv = BackendServer(my_port, peers)
    srv.run()