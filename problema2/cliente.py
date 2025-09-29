#!/usr/bin/env python3
"""
Problema 2: Comunicación bidireccional - Cliente
Objetivo: Crear un cliente TCP que envíe un mensaje al servidor y reciba la misma respuesta
"""

import socket

#  Definir la dirección y puerto del servidor
HOST = 'localhost'
PORT = 9000

# Solicitar mensaje al usuario por consola
mensaje = input("Digita tu mensaje: ")

#  Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al servidor en la dirección y puerto especificados
client.connect((HOST, PORT))

# Mostrar mensaje que se va a enviar
print(f"Mensaje '{mensaje}' enviado.")

# Codificar el mensaje a bytes y enviarlo al servidor
# sendall() asegura que todos los datos sean enviados
client.sendall(mensaje.encode())

# Recibir datos del servidor (hasta 1024 bytes)
data = client.recv(1024)


# Decodificar e imprimir los datos recibidos
print("Mensaje recibido: ", data.decode())

#  Cerrar la conexión con el servidor
client.close()
