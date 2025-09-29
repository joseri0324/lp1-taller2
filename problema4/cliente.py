#!/usr/bin/env python3
"""
Problema 4: Servidor HTTP básico - Cliente
Objetivo: Crear un cliente HTTP que realice una petición GET a un servidor web local
"""

import http.client
import socket

# Definir la dirección y puerto del servidor HTTP
HOST = 'localhost'
PORT = 8080

# Crear una conexión HTTP con el servidor
# HTTPConnection permite establecer conexiones HTTP con servidores
def run_client():
    client = http.client.HTTPConnection(HOST, PORT)

# Realizar una petición GET al path raíz ('/')
# request() envía la petición HTTP al servidor
# Primer parámetro: método HTTP (GET, POST, etc.)
# Segundo parámetro: path del recurso solicitado
    client.request("GET", "/")

# Obtener la respuesta del servidor
# getresponse() devuelve un objeto HTTPResponse con los datos de la respuesta
    response = client.getresponse()
    print(f"Status: {response.status}, Reason: {response.reason}")
    print("Headers:")
    for header, value in response.getheaders():
        print(f"{header}: {value}")

# Leer el contenido de la respuesta
# read() devuelve el cuerpo de la respuesta en bytes
    body = response.read().decode("utf-8")
    print("Contenido recibido: ")
    print(body)

# Decodificar los datos de bytes a string e imprimirlos
# decode() convierte los bytes a string usando UTF-8 por defecto

# Cerrar la conexión con el servidor
    client.close()

if __name__ == "__main__":
    run_client()