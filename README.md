# Taller de Programación en Redes con Python (Sockets, Cliente-Servidor)

Este repositorio contiene **9 problemas** progresivos para que un estudiante desarrolle intuición y práctica en el uso de **Programación en Redes** con Python, enfocándose en comunicación cliente-servidor usando sockets.

## Conceptos clave del taller

- **Sockets TCP/UDP**: Los **sockets** son los puntos finales de una comunicación bidireccional en una red. **TCP** (Transmission Control Protocol) es un protocolo orientado a la conexión, fiable y con control de flujo, ideal para aplicaciones que requieren integridad de datos (como transferencia de archivos). **UDP** (User Datagram Protocol) es un protocolo sin conexión, rápido y con baja latencia, adecuado para aplicaciones donde la velocidad es más importante que la fiabilidad (como el streaming de video).

- **Protocolos**: Un **protocolo** es un conjunto de reglas para la comunicación de datos entre dos o más dispositivos. **HTTP** (Hypertext Transfer Protocol) es el protocolo estándar para la web. También se pueden crear **protocolos personalizados** para necesidades específicas, y el **message framing** es la técnica para delimitar mensajes dentro de un flujo de datos continuo.

- **Serialización**: La **serialización** es el proceso de convertir un objeto de datos complejo en un formato que puede ser almacenado o transmitido (como un string o un archivo binario). **JSON** (JavaScript Object Notation) es un formato de texto muy popular, mientras que **pickle** es un módulo de Python para serializar objetos de forma nativa.

- **Concurrencia**: La **concurrencia** es la capacidad de un programa para gestionar múltiples tareas al mismo tiempo. **Threading** es ideal para tareas que consumen mucho tiempo de CPU, mientras que **asyncio** es una librería que usa la programación asíncrona para manejar de forma eficiente tareas intensivas en **I/O** (Input/Output), como esperar una respuesta de red sin bloquear otros procesos.

- **Threading**: El **threading** es una técnica que permite a un programa ejecutar múltiples hilos de ejecución simultáneamente. Se usa para manejar tareas concurrentes y puede ser útil en servidores para atender a varios clientes al mismo tiempo sin bloquear el programa principal.

- **Manejo de errores**: El **manejo de errores** es crucial para crear aplicaciones robustas. Implica anticipar y gestionar fallos comunes como **conexiones perdidas**, **timeouts** (cuando una operación tarda demasiado en completarse) y **excepciones** de código que podrían ocurrir durante la comunicación.

- **Seguridad básica**: La **seguridad básica** en la programación de red implica proteger tu aplicación de posibles ataques o usos indebidos. Esto incluye la **validación de entrada** para asegurar que los datos recibidos sean seguros y la **limitación de recursos** para prevenir ataques de denegación de servicio (DoS) que agoten los recursos del servidor.

## Cómo desarrollar el taller

1. Prepara el ambiente de desarrollo con Python 3.9+ o superior instalado.

2. Ingresa a `https://github.com/UR-CC/lp1-taller2` y realiza un **fork** con tu cuenta.

3. Clona tu **fork** del repositorio `lp1-taller2`:

    ```bash
    git clone https://github.com/TU-USUARIO/lp1-taller2.git
    cd lp1-taller2
    ```

4. Para ejecutar cada problema, necesitas tener **dos terminales** abiertas, una para el **servidor** y otra para el **cliente**:

    **Terminal 1**: Servidor

    ```bash
    python problema1/servidor.py
    ```
    
    **Terminal 2**: Cliente
    ```bash
    python problema1/cliente.py
    ```

5. Para cada problema, busca los comentarios `# TODO:` y sigue las indicaciones.

6. Para probar con múltiples clientes simultáneamente, puedes abrir terminales adicionales y ejecutar de nuevo el cliente en cada una.

**Nota**: Puedes seguir el desarrollo paso a paso de [los primeros 4 problemas en este video](https://www.youtube.com/watch?v=kPXa73a0kCA).

---

## Contenido

### Problema 1 – Sockets básicos (Conexión simple)

Comprender los conceptos fundamentales de sockets TCP: crear servidor, aceptar conexiones, enviar y recibir datos básicos.

### Problema 2 – Servidor Echo (Repetir mensajes)

Implementar un servidor que devuelve exactamente lo que el cliente envía. Practicar el ciclo básico de comunicación bidireccional.

### Problema 3 – Chat simple (Múltiples clientes)

Crear un servidor de chat básico que permite a múltiples clientes conectarse y enviarse mensajes entre sí usando threading.

### Problema 4 – Servidor HTTP básico (Protocolo HTTP)

Implementar un servidor web simple que responda peticiones HTTP GET, sirviendo archivos estáticos y comprendiendo headers HTTP.

### Problema 5 – Transferencia de archivos (Upload/Download)

Construir un servidor que permita subir y descargar archivos, manejando datos binarios y control de flujo.

### Problema 6 – Chat con salas (Gestión de grupos)

Extender el chat para soportar múltiples salas/canales, con comandos para unirse, salir y listar salas disponibles.

### Problema 7 – Proxy HTTP (Intermediario de red)

Crear un proxy que intercepte peticiones HTTP del cliente, las reenvíe al servidor destino y retorne la respuesta.

### Problema 8 – Servidor de juegos (Estado compartido)

Implementar un juego simple multijugador (tic-tac-toe) que mantenga estado del juego y coordine turnos entre jugadores.

### Problema 9 – Sistema distribuido (Coordinación entre servidores)

Construir un sistema con múltiples servidores que se comunican entre sí para balancear carga o replicar datos.

---

## Recomendaciones

- Para cada problema, empieza por leer todos los comentarios `# TODO:` antes de empezar a modificar el código.
- Prueba primero con un solo cliente, luego con múltiples clientes.
- Usa herramientas como `telnet` o `curl` para probar tus servidores.
- Agrega logs con `print()` para entender el flujo de ejecución.
- Maneja excepciones apropiadamente para conexiones que se cierran inesperadamente.
- Para problemas avanzados, considera usar `select()` o `asyncio` para manejar múltiples conexiones eficientemente.

## Herramientas útiles

* Verificar puertos en uso

    ```bash
    netstat -tuln | grep :8000
    ```

* Conectar con telnet para pruebas

    ```bash
    telnet localhost 8000
    ```

* Hacer peticiones HTTP

    ```bash
    curl -X GET http://localhost:8000
    wget -O - http://localhost:8000
    printf "GET / HTTP/1.1\r\nHost: localhost:8000\r\n\r\n" | nc localhost 8000
    ```

* Monitorear tráfico de red

    ```bash
    tcpdump -i lo port 8000
    ```

* Monitorear conexiones

    ```bash
    ss -tuln | grep :800
    ```

