#!/usr/bin/env python3
"""
Problema 2: Comunicación bidireccional - Cliente
Objetivo: Crear un cliente TCP que envíe un mensaje al servidor y reciba la misma respuesta
"""

import socket

# TODO: Definir la dirección y puerto del servidor

# Solicitar mensaje al usuario por consola
message = input("Mensaje: ")

# TODO: Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)

# TODO: Conectar el socket al servidor en la dirección y puerto especificados

# Mostrar mensaje que se va a enviar
print(f"Mensaje '{message}' enviado.")

# TODO: Codificar el mensaje a bytes y enviarlo al servidor
# sendall() asegura que todos los datos sean enviados

# TODO: Recibir datos del servidor (hasta 1024 bytes)

# Decodificar e imprimir los datos recibidos
print("Mensaje recibido: ", data.decode())

# TODO: Cerrar la conexión con el servidor

