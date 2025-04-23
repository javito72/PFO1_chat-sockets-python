import socket
import sqlite3
import datetime
import threading
import sys

def inicializar_bd():
    """
    Inicializa la base de datos y crea la tabla de mensajes si no existe.
    """
    try:
        # Conectar a la base de datos (se creará si no existe)
        conexion = sqlite3.connect('chat.db')
        cursor = conexion.cursor()
        
        # Crear tabla de mensajes si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TIMESTAMP NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        ''')
        
        conexion.commit()
        conexion.close()
        print("[INFO] Base de datos inicializada correctamente.")
        return True
    except sqlite3.Error as e:
        print(f"[ERROR] Error al inicializar la base de datos: {e}")
        return False

def guardar_mensaje(contenido, ip_cliente):
    """
    Guarda un mensaje en la base de datos.
    
    Args:
        contenido (str): El contenido del mensaje
        ip_cliente (str): La dirección IP del cliente
        
    Returns:
        bool: True si el mensaje se guardó correctamente, False en caso contrario
    """
    try:
        # Obtener fecha y hora actual
        fecha_envio = datetime.datetime.now()
        
        # Conectar a la base de datos
        conexion = sqlite3.connect('chat.db')
        cursor = conexion.cursor()
        
        # Insertar mensaje en la tabla
        cursor.execute('''
            INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
            VALUES (?, ?, ?)
        ''', (contenido, fecha_envio, ip_cliente))
        
        conexion.commit()
        conexion.close()
        print(f"[INFO] Mensaje guardado: {contenido} | De: {ip_cliente}")
        return True, fecha_envio
    except sqlite3.Error as e:
        print(f"[ERROR] Error al guardar el mensaje: {e}")
        return False, None

def inicializar_socket():
    """
    Inicializa y configura el socket del servidor.
    
    Returns:
        socket: El socket del servidor configurado
    """
    try:
        # Configuración del socket TCP/IP
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Permitir reutilizar la dirección
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Dirección y puerto para escuchar
        direccion_servidor = ('localhost', 5000)
        
        # Enlazar el socket al puerto
        servidor.bind(direccion_servidor)
        
        # Escuchar conexiones entrantes (máximo 5 en cola)
        servidor.listen(5)
        
        print(f"[INFO] Servidor escuchando en {direccion_servidor[0]}:{direccion_servidor[1]}")
        return servidor
    except socket.error as e:
        print(f"[ERROR] Error al inicializar el socket: {e}")
        sys.exit(1)

def manejar_cliente(conexion_cliente, direccion_cliente):
    """
    Maneja la comunicación con un cliente.
    
    Args:
        conexion_cliente (socket): La conexión con el cliente
        direccion_cliente (tuple): La dirección del cliente (IP, puerto)
    """
    ip_cliente = direccion_cliente[0]
    puerto_cliente = direccion_cliente[1]
    
    print(f"[INFO] Conexión establecida con {ip_cliente}:{puerto_cliente}")
    
    try:
        while True:
            # Recibir datos del cliente
            datos = conexion_cliente.recv(1024)
            if not datos:
                break
            
            # Decodificar el mensaje
            mensaje = datos.decode('utf-8')
            print(f"[INFO] Mensaje recibido de {ip_cliente}: {mensaje}")
            
            # Guardar el mensaje en la base de datos
            resultado, timestamp = guardar_mensaje(mensaje, ip_cliente)
            
            # Preparar respuesta para el cliente
            if resultado:
                respuesta = f"Mensaje recibido: {timestamp}"
            else:
                respuesta = "Error al procesar el mensaje"
            
            # Enviar respuesta al cliente
            conexion_cliente.sendall(respuesta.encode('utf-8'))
            
    except socket.error as e:
        print(f"[ERROR] Error en la comunicación con {ip_cliente}: {e}")
    finally:
        # Cerrar la conexión
        conexion_cliente.close()
        print(f"[INFO] Conexión cerrada con {ip_cliente}:{puerto_cliente}")

def aceptar_conexiones(servidor_socket):
    """
    Acepta conexiones entrantes y crea un hilo para manejar cada cliente.
    
    Args:
        servidor_socket (socket): El socket del servidor
    """
    try:
        while True:
            # Esperar por una conexión
            conexion_cliente, direccion_cliente = servidor_socket.accept()
            
            # Crear un hilo para manejar al cliente
            hilo_cliente = threading.Thread(
                target=manejar_cliente,
                args=(conexion_cliente, direccion_cliente)
            )
            hilo_cliente.daemon = True
            hilo_cliente.start()
            
    except KeyboardInterrupt:
        print("\n[INFO] Servidor detenido por el usuario")
    except Exception as e:
        print(f"[ERROR] Error al aceptar conexiones: {e}")
    finally:
        # Cerrar el socket del servidor
        servidor_socket.close()
        print("[INFO] Socket del servidor cerrado")

def main():
    """
    Función principal que inicia el servidor.
    """
    print("[INFO] Iniciando servidor de chat...")
    
    # Inicializar la base de datos
    if not inicializar_bd():
        print("[ERROR] No se pudo inicializar la base de datos. Saliendo...")
        sys.exit(1)
    
    # Inicializar el socket
    servidor_socket = inicializar_socket()
    
    # Aceptar conexiones
    aceptar_conexiones(servidor_socket)

if __name__ == "__main__":
    main()
