#!/usr/bin/env python3
"""
Problema 1: Sockets básicos - Servidor
Objetivo: Crear un servidor TCP que acepte una conexión y intercambie mensajes básicos
"""

import socket



# Definir la dirección y puerto del servidor
HOST = 'localhost'
PORT = 9000

# Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


#  Enlazar el socket a la dirección y puerto especificados
servidor.bind((HOST, PORT))

# Poner el socket en modo escucha
# El parámetro define el número máximo de conexiones en cola
servidor.listen()

print("Servidor a la espera de conexiones ...")

# Aceptar una conexión entrante
# accept() bloquea hasta que llega una conexión
# conn: nuevo socket para comunicarse con el cliente
# addr: dirección y puerto del cliente
conn, addr = servidor.accept()

print(f"Conexión realizada por {addr}")

# Recibir datos del cliente (hasta 1024 bytes)
datos = conn.recv(1024)
print("Mensaje recibido del cliente:", datos.decode('utf-8'))
 
# Enviar respuesta al cliente (convertida a bytes)
# sendall() asegura que todos los datos sean enviados
respuesta = "Hola cliente, mensaje recibido correctamente"
conn.sendall(respuesta.encode('utf-8'))

# Cerrar la conexión con el cliente
conn.close()
