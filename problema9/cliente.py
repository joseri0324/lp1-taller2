#!/usr/bin/env python3
import sys
import http.client

HOST = "localhost"
PORT = 9500  # ajusta al puerto de tu load balancer

def put(key, value):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Length": str(len(value))}
    conn.request("POST", f"/put/{key}", body=value, headers=headers)
    r = conn.getresponse()
    body = r.read()  # aquí no fallará porque Content-Length ya está correcto
    print("PUT", r.status, r.reason, body.decode())
    conn.close()

def get(key):
    conn = http.client.HTTPConnection(HOST, PORT)
    conn.request("GET", f"/get/{key}")
    r = conn.getresponse()
    body = r.read()
    print("GET", r.status, r.reason, body.decode())
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: client.py <get|put> <key> [value]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "put":
        put(sys.argv[2], sys.argv[3])
    elif cmd == "get":
        get(sys.argv[2])
    else:
        print("Comando inválido")