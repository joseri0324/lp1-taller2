#!/usr/bin/env python3
"""
Problema 2: Comunicación bidireccional - Servidor
Objetivo: Crear un servidor TCP que devuelva exactamente lo que recibe del cliente
"""

import socket

# Definir la dirección y puerto del servidor
HOST = 'localhost'
PORT = 9000

# Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Enlazar el socket a la dirección y puerto especificados
servidor.bind((HOST, PORT))

#Poner el socket en modo escucha
# El parámetro define el número máximo de conexiones en cola
servidor.listen()

# Bucle infinito para manejar múltiples conexiones (una a la vez)
while True:

    print("El Servidor 'Echo' está  esperando conexiones ...")
    
    # Aceptar una conexión entrante
    # accept() bloquea hasta que llega una conexión
    # conn: nuevo socket para comunicarse con el cliente
    # addr: dirección y puerto del cliente
    cliente, direccion = servidor.accept()


    print(f"Un cliente se conecto dese la dirección {direccion}")
    

    # Recibir datos del cliente (hasta 1024 bytes)
    datos = cliente.recv(1024)
    
    # Si no se reciben datos, salir del bucle
    if not datos:
        break

    # Mostrar los datos recibidos (en formato bytes)
    print("Datos recibidos:", datos)
    
    # Enviar los mismos datos de vuelta al cliente (echo)
    cliente.sendall(datos)

    # Cerrar la conexión con el cliente actual
    cliente.close()

