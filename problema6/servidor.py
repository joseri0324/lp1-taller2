#!/usr/bin/env python3
"""
Servidor de chat con salas (JOIN, LEAVE, CREATE, LIST, USERS, MSG).
Cada cliente se maneja en un hilo separado.
"""

import socket
import threading
import json
import os

HOST = "localhost"
PORT = 9300
BUFFER = 4096
STATE_FILE = "salas.json"

# ----------------- ESTADO GLOBAL -----------------
salas = {}       # {"sala1": {"usuarios": set(["Dani", "Ana"])}, ...}
clientes = {}    # {conn: {"nombre": "Dani", "sala": "sala1"}}
lock = threading.Lock()  # Para sincronizar acceso a salas/clientes


# ----------------- PERSISTENCIA -----------------
def cargar_salas():
    """Carga las salas desde un archivo JSON si existe"""
    global salas
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            salas = json.load(f)
            # Convertir listas a sets
            for sala in salas.values():
                sala["usuarios"] = set(sala["usuarios"])
    else:
        salas = {"general": {"usuarios": set()}}  # Sala por defecto


def guardar_salas():
    """Guarda las salas y usuarios en un archivo JSON"""
    with lock:
        data = {k: {"usuarios": list(v["usuarios"])} for k, v in salas.items()}
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)


# ----------------- FUNCIONES AUXILIARES -----------------
def enviar(conn, msg):
    """Envía un mensaje con salto de línea"""
    conn.sendall((msg + "\n").encode())


def broadcast(sala, remitente, mensaje):
    """Envía un mensaje a todos los usuarios de una sala"""
    with lock:
        for c, info in clientes.items():
            if info["sala"] == sala and c != remitente:
                try:
                    enviar(c, f"[{info['sala']}] {clientes[remitente]['nombre']}: {mensaje}")
                except:
                    pass


def privado(destinatario, remitente, mensaje):
    """Envía un mensaje privado a un usuario"""
    with lock:
        for c, info in clientes.items():
            if info["nombre"] == destinatario:
                enviar(c, f"[PRIVADO de {clientes[remitente]['nombre']}] {mensaje}")
                return True
    return False


# ----------------- HILO POR CLIENTE -----------------
def manejar_cliente(conn, addr):
    try:
        enviar(conn, "Bienvenido al chat. Ingresa tu nombre de usuario:")
        nombre = conn.recv(BUFFER).decode().strip()

        with lock:
            clientes[conn] = {"nombre": nombre, "sala": "general"}
            salas["general"]["usuarios"].add(nombre)

        enviar(conn, f"Hola {nombre}! Te uniste a la sala 'general'.")
        broadcast("general", conn, f"⚡ {nombre} se ha unido a la sala.")

        while True:
            data = conn.recv(BUFFER)
            if not data:
                break

            msg = data.decode().strip()
            if not msg:
                continue

            parts = msg.split(" ", 2)
            comando = parts[0].upper()

            # ---- COMANDOS ----
            if comando == "CREATE" and len(parts) > 1:
                sala = parts[1]
                with lock:
                    if sala not in salas:
                        salas[sala] = {"usuarios": set()}
                        enviar(conn, f"Sala '{sala}' creada.")
                        guardar_salas()
                    else:
                        enviar(conn, "ERR: Sala ya existe.")

            elif comando == "JOIN" and len(parts) > 1:
                sala = parts[1]
                with lock:
                    if sala not in salas:
                        enviar(conn, "ERR: Sala no existe.")
                    else:
                        old = clientes[conn]["sala"]
                        salas[old]["usuarios"].discard(nombre)
                        clientes[conn]["sala"] = sala
                        salas[sala]["usuarios"].add(nombre)
                        enviar(conn, f"Te uniste a la sala '{sala}'.")
                        broadcast(sala, conn, f"⚡ {nombre} entró en la sala.")
                        guardar_salas()

            elif comando == "LEAVE":
                with lock:
                    sala = clientes[conn]["sala"]
                    salas[sala]["usuarios"].discard(nombre)
                    clientes[conn]["sala"] = "general"
                    salas["general"]["usuarios"].add(nombre)
                enviar(conn, "Volviste a la sala 'general'.")

            elif comando == "LIST":
                with lock:
                    enviar(conn, "Salas disponibles:")
                    for s in salas.keys():
                        enviar(conn, f" - {s}")

            elif comando == "USERS":
                with lock:
                    sala = clientes[conn]["sala"]
                    usuarios = ", ".join(salas[sala]["usuarios"])
                    enviar(conn, f"Usuarios en {sala}: {usuarios}")

            elif comando == "MSG" and len(parts) > 2:
                destinatario, texto = parts[1], parts[2]
                if not privado(destinatario, conn, texto):
                    enviar(conn, "ERR: Usuario no encontrado.")

            elif comando == "QUIT":
                enviar(conn, "Adiós!")
                break

            else:
                # Mensaje normal → broadcast en sala actual
                sala = clientes[conn]["sala"]
                broadcast(sala, conn, msg)

    except Exception as e:
        print(f"Error con {addr}: {e}")
    finally:
        # Cleanup al salir
        with lock:
            if conn in clientes:
                sala = clientes[conn]["sala"]
                nombre = clientes[conn]["nombre"]
                salas[sala]["usuarios"].discard(nombre)
                del clientes[conn]
                guardar_salas()
        conn.close()


# ----------------- MAIN -----------------
def main():
    cargar_salas()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escuchando en {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()