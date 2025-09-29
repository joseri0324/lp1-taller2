#!/usr/bin/env python3
"""
Cliente simple para Tic-Tac-Toe (problema8/cliente.py)

- Interactivo: pide nombre, luego acepta comandos desde stdin.
- Muestra mensajes que el servidor envía.
"""
import socket
import threading
import sys

HOST = 'localhost'
PORT = 9401
BUFFER = 4096

def receiver(sock):
    """Hilo que imprime todo lo que llega del servidor."""
    try:
        while True:
            data = sock.recv(BUFFER)
            if not data:
                print("Conexión cerrada por servidor")
                break
            print(data.decode().strip())
    except Exception:
        pass
    finally:
        sock.close()

def main():
    sock = socket.create_connection((HOST, PORT))
    # hilo que escucha
    threading.Thread(target=receiver, args=(sock,), daemon=True).start()

    # enviar nombre
    name = input("Tu nombre: ").strip()
    sock.sendall((name + "\n").encode())

    print("Comandos disponibles:")
    print(" CREATE_MATCH")
    print(" LIST_MATCHES")
    print(" JOIN_MATCH <id>")
    print(" MOVE <id> <pos>     (pos 0..8)")
    print(" SPECTATE <id>")
    print(" QUIT")

    try:
        while True:
            line = input("> ").strip()
            if not line:
                continue
            sock.sendall((line + "\n").encode())
            if line.upper() == "QUIT":
                break
    except KeyboardInterrupt:
        sock.sendall(b"QUIT\n")
    finally:
        sock.close()

if __name__ == "__main__":
    main()