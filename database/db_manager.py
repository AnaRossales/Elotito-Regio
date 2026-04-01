# database/db_manager.py
# Contiene todas las funciones que interactúan con la base de datos.

import mysql.connector
from mysql.connector import Error
from models.cliente import Cliente
from models.paquete import Paquete
from models.evento import Evento

def crear_conexion():
    """Crea y retorna una conexión a la base de datos MySQL."""
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            database='elotito_regio_db',
            user='root',
            password=''  # <-- Asegúrate de que esta sea tu contraseña (vacía para XAMPP por defecto)
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

# --- Funciones de Clientes ---

def agregar_cliente_db(conexion, cliente):
    """Registra un nuevo cliente en la BD. Recibe un objeto Cliente."""
    cursor = None
    try:
        cursor = conexion.cursor()
        sql = """
        INSERT INTO Clientes (nombre, telefono, email, direccion, fecha_registro)
        VALUES (%s, %s, %s, %s, %s)
        """
        valores = (cliente.nombre, cliente.telefono, cliente.email, 
                   cliente.direccion, cliente.fecha_registro)
        cursor.execute(sql, valores)
        conexion.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al registrar cliente: {e}")
        return None
    finally:
        if cursor: cursor.close()

def get_clientes_db(conexion):
    """Obtiene todos los clientes de la BD. Devuelve una lista de objetos Cliente."""
    clientes = []
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_cliente, nombre, telefono, email, direccion, fecha_registro FROM Clientes")
        for fila in cursor.fetchall():
            cliente = Cliente(
                id_cliente=fila[0], nombre=fila[1], telefono=fila[2],
                email=fila[3], direccion=fila[4], fecha_registro=fila[5]
            )
            clientes.append(cliente)
    except Error as e:
        print(f"Error al consultar clientes: {e}")
    finally:
        if cursor: cursor.close()
    return clientes

# --- Funciones de Paquetes ---

def agregar_paquete_db(conexion, paquete):
    """Registra un nuevo paquete en la BD. Recibe un objeto Paquete."""
    cursor = None
    try:
        cursor = conexion.cursor()
        sql = "INSERT INTO Paquetes (nombre_paquete, descripcion, precio) VALUES (%s, %s, %s)"
        valores = (paquete.nombre_paquete, paquete.descripcion, paquete.precio)
        cursor.execute(sql, valores)
        conexion.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al registrar paquete: {e}")
        return None
    finally:
        if cursor: cursor.close()

def get_paquetes_db(conexion):
    """Obtiene todos los paquetes. Devuelve una lista de objetos Paquete."""
    paquetes = []
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_paquete, nombre_paquete, descripcion, precio FROM Paquetes")
        for fila in cursor.fetchall():
            paquete = Paquete(
                id_paquete=fila[0], nombre=fila[1],
                descripcion=fila[2], precio=fila[3]
            )
            paquetes.append(paquete)
    except Error as e:
        print(f"Error al consultar paquetes: {e}")
    finally:
        if cursor: cursor.close()
    return paquetes

# --- Funciones de Eventos ---

def agregar_evento_db(conexion, evento):
    """
    Registra un nuevo evento y sus paquetes asociados en una transacción.
    Recibe un objeto Evento.
    """
    cursor = None
    try:
        cursor = conexion.cursor()
        
        # --- AQUÍ ESTABA EL ERROR ---
        # La línea 'conexion.start_transaction()' fue eliminada.
        
        # 1. Insertar en la tabla Eventos
        sql_evento = """
        INSERT INTO Eventos (id_cliente, fecha_evento, hora_evento, lugar, adelanto, total, metodo_pago)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores_evento = (evento.id_cliente, evento.fecha_evento, evento.hora_evento, 
                          evento.lugar, evento.adelanto, evento.total, evento.metodo_pago)
        
        cursor.execute(sql_evento, valores_evento)
        id_evento_nuevo = cursor.lastrowid
        
        # 2. Insertar en la tabla Evento_Paquete
        sql_paquete = "INSERT INTO Evento_Paquete (id_evento, id_paquete, cantidad) VALUES (%s, %s, %s)"
        
        for (id_paquete, cantidad) in evento.paquetes:
            valores_paquete = (id_evento_nuevo, id_paquete, cantidad)
            cursor.execute(sql_paquete, valores_paquete)

        # Si todo salió bien, confirmar la transacción
        conexion.commit()
        return id_evento_nuevo

    except Error as e:
        # Aquí se imprime tu error
        print(f"Error al registrar evento: {e}")
        # Si algo falla, revertir todos los cambios
        if conexion: conexion.rollback()
        return None
    finally:
        if cursor: cursor.close()

def get_eventos_db(conexion):
    """
    Obtiene un listado simple de eventos con el nombre del cliente.
    """
    eventos = []
    cursor = None
    try:
        cursor = conexion.cursor()
        # Unimos Eventos con Clientes para obtener el nombre
        sql = """
        SELECT e.id_evento, e.fecha_evento, e.lugar, c.nombre 
        FROM Eventos e
        JOIN Clientes c ON e.id_cliente = c.id_cliente
        ORDER BY e.fecha_evento DESC
        """
        cursor.execute(sql)
        for (id_evento, fecha, lugar, cliente_nombre) in cursor.fetchall():
            eventos.append({
                "id": id_evento,
                "fecha": fecha,
                "lugar": lugar,
                "cliente": cliente_nombre
            })
    except Error as e:
        print(f"Error al consultar eventos: {e}")
    finally:
        if cursor: cursor.close()
    return eventos