import socket
import sys

def conectar_servidor():
    """
    Establece conexión con el servidor.
    
    Returns:
        socket: El socket conectado al servidor o None si hay error
    """
    try:
        # Configuración del socket TCP/IP
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Dirección y puerto del servidor
        direccion_servidor = ('localhost', 5000)
        
        # Conectar al servidor
        print(f"[INFO] Conectando al servidor {direccion_servidor[0]}:{direccion_servidor[1]}...")
        cliente.connect(direccion_servidor)
        
        print("[INFO] Conexión establecida con el servidor")
        return cliente
    except socket.error as e:
        print(f"[ERROR] Error al conectar con el servidor: {e}")
        return None

def enviar_mensaje(cliente_socket, mensaje):
    """
    Envía un mensaje al servidor y recibe la respuesta.
    
    Args:
        cliente_socket (socket): El socket conectado al servidor
        mensaje (str): El mensaje a enviar
        
    Returns:
        str: La respuesta del servidor o None si hay error
    """
    try:
        # Enviar mensaje al servidor
        cliente_socket.sendall(mensaje.encode('utf-8'))
        
        # Recibir respuesta del servidor
        respuesta = cliente_socket.recv(1024).decode('utf-8')
        return respuesta
    except socket.error as e:
        print(f"[ERROR] Error al enviar/recibir mensaje: {e}")
        return None

def main():
    """
    Función principal que inicia el cliente.
    """
    print("[INFO] Iniciando cliente de chat...")
    
    # Conectar al servidor
    cliente_socket = conectar_servidor()
    if not cliente_socket:
        print("[ERROR] No se pudo establecer conexión con el servidor. Saliendo...")
        sys.exit(1)
    
    try:
        print("========== CHAT CLIENTE ==========")
        print("Escribe 'exit' para salir")
        
        # Bucle principal para enviar mensajes
        while True:
            # Obtener mensaje del usuario
            mensaje = input("Mensaje: ")
            
            # Verificar si el usuario quiere salir
            if mensaje.lower() == 'exit':
                print("[INFO] Cerrando conexión...")
                break
            
            # Enviar mensaje al servidor
            respuesta = enviar_mensaje(cliente_socket, mensaje)
            
            # Mostrar respuesta del servidor
            if respuesta:
                print(f"Servidor: {respuesta}")
            else:
                print("[ERROR] No se recibió respuesta del servidor")
                break
    
    except KeyboardInterrupt:
        print("\n[INFO] Cliente detenido por el usuario")
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
    finally:
        # Cerrar el socket del cliente
        cliente_socket.close()
        print("[INFO] Conexión cerrada")

if __name__ == "__main__":
    main()
