#!/usr/bin/env python3
"""
Cliente interactivo para el chat con salas.
"""

import socket
import threading

HOST = "localhost"
PORT = 9300
BUFFER = 4096


def recibir(conn):
    """Hilo para escuchar mensajes del servidor"""
    while True:
        try:
            data = conn.recv(BUFFER)
            if not data:
                break
            print(data.decode().strip())
        except:
            break


def main():
    conn = socket.create_connection((HOST, PORT))

    # Hilo separado para recibir mensajes
    threading.Thread(target=recibir, args=(conn,), daemon=True).start()

    try:
        while True:
            msg = input()
            if not msg:
                continue
            conn.sendall((msg + "\n").encode())
            if msg.upper() == "QUIT":
                break
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()


if __name__ == "__main__":
    main()