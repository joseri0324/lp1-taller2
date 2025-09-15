#!/usr/bin/env python3
"""
Problema 2: Comunicación bidireccional - Servidor
Objetivo: Crear un servidor TCP que devuelva exactamente lo que recibe del cliente
"""

import socket

# TODO: Definir la dirección y puerto del servidor

# TODO: Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)

# TODO: Enlazar el socket a la dirección y puerto especificados

# TODO: Poner el socket en modo escucha
# El parámetro define el número máximo de conexiones en cola

# Bucle infinito para manejar múltiples conexiones (una a la vez)
while True:

    print("Servidor a la espera de conexiones ...")
    
    # TODO: Aceptar una conexión entrante
    # accept() bloquea hasta que llega una conexión
    # conn: nuevo socket para comunicarse con el cliente
    # addr: dirección y puerto del cliente
    
    print(f"Conexión realizada por {addr}")

    # TODO: Recibir datos del cliente (hasta 1024 bytes)
    
    # Si no se reciben datos, salir del bucle
    if not data:
        break

    # Mostrar los datos recibidos (en formato bytes)
    print("Datos recibidos:", data)
    
    # TODO: Enviar los mismos datos de vuelta al cliente (echo)
    
    # TODO: Cerrar la conexión con el cliente actual

