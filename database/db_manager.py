# database/db_manager.py
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
            password='' 
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

# -----------------------------------------------------------------
# --- Funciones de Clientes ---
# -----------------------------------------------------------------
def agregar_cliente_db(conexion, cliente):
    cursor = None
    try:
        cursor = conexion.cursor()
        sql = """
        INSERT INTO Clientes (nombre, apellido_paterno, apellido_materno, telefono, email) 
        VALUES (%s, %s, %s, %s, %s)
        """
        valores = (cliente.nombre, cliente.apellido_paterno, cliente.apellido_materno, 
                   cliente.telefono, cliente.email)
        cursor.execute(sql, valores)
        conexion.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al registrar cliente: {e}")
        return None
    finally:
        if cursor: cursor.close()

def get_clientes_db(conexion):
    clientes = []
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_cliente, nombre, apellido_paterno, apellido_materno, telefono, email FROM Clientes")
        for fila in cursor.fetchall():
            cliente = Cliente(id_cliente=fila[0], nombre=fila[1], apellido_paterno=fila[2], 
                              apellido_materno=fila[3], telefono=fila[4], email=fila[5])
            clientes.append(cliente)
    except Error as e:
        print(f"Error al consultar clientes: {e}")
    finally:
        if cursor: cursor.close()
    return clientes

# -----------------------------------------------------------------
# --- Funciones de Paquetes (¡Las que faltaban!) ---
# -----------------------------------------------------------------
def agregar_paquete_db(conexion, paquete):
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

# -----------------------------------------------------------------
# --- Funciones de Eventos y Catálogos ---
# -----------------------------------------------------------------
def get_metodos_pago_db(conexion):
    metodos = []
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_metodo, nombre_metodo FROM Metodos_Pago")
        for fila in cursor.fetchall():
            metodos.append({"id": fila[0], "nombre": fila[1]})
    except Error as e:
        print(f"Error al consultar metodos de pago: {e}")
    finally:
        if cursor: cursor.close()
    return metodos

def agregar_evento_db(conexion, evento):
    cursor = None
    try:
        cursor = conexion.cursor()
        sql_evento = """
        INSERT INTO Eventos (id_cliente, fecha_evento, hora_evento, lugar, adelanto, id_metodo_pago)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores_evento = (evento.id_cliente, evento.fecha_evento, evento.hora_evento, 
                          evento.lugar, evento.adelanto, evento.id_metodo_pago)
        
        cursor.execute(sql_evento, valores_evento)
        id_evento_nuevo = cursor.lastrowid
        
        sql_paquete = "INSERT INTO Evento_Paquete (id_evento, id_paquete, cantidad) VALUES (%s, %s, %s)"
        for (id_paquete, cantidad) in evento.paquetes:
            cursor.execute(sql_paquete, (id_evento_nuevo, id_paquete, cantidad))

        conexion.commit()
        return id_evento_nuevo
    except Error as e:
        print(f"Error al registrar evento: {e}")
        if conexion: conexion.rollback()
        return None
    finally:
        if cursor: cursor.close()

def get_eventos_db(conexion):
    eventos = []
    cursor = None
    try:
        cursor = conexion.cursor()
        sql = """
        SELECT 
            e.id_evento, e.fecha_evento, e.lugar, 
            CONCAT(c.nombre, ' ', c.apellido_paterno) as cliente,
            IFNULL(m.nombre_metodo, 'N/A') as metodo_pago,
            e.adelanto,
            IFNULL(SUM(ep.cantidad * p.precio), 0) as total_evento
        FROM Eventos e
        JOIN Clientes c ON e.id_cliente = c.id_cliente
        LEFT JOIN Metodos_Pago m ON e.id_metodo_pago = m.id_metodo
        LEFT JOIN Evento_Paquete ep ON e.id_evento = ep.id_evento
        LEFT JOIN Paquetes p ON ep.id_paquete = p.id_paquete
        GROUP BY e.id_evento
        ORDER BY e.fecha_evento DESC
        """
        cursor.execute(sql)
        for fila in cursor.fetchall():
            eventos.append({
                "id": fila[0], "fecha": fila[1], "lugar": fila[2], "cliente": fila[3],
                "metodo_pago": fila[4], "adelanto": fila[5], "total": fila[6]
            })
    except Error as e:
        print(f"Error al consultar eventos: {e}")
    finally:
        if cursor: cursor.close()
    return eventos