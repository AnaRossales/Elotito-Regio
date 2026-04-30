import mysql.connector
from mysql.connector import Error
from models.cliente import Cliente
from models.paquete import Paquete
from models.evento import Evento

def crear_conexion():
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

# --- Clientes ---
def agregar_cliente_db(conexion, cliente):
    cursor = None
    try:
        cursor = conexion.cursor()
        sql = "INSERT INTO Clientes (nombre, apellido_paterno, apellido_materno, telefono, email) VALUES (%s, %s, %s, %s, %s)"
        valores = (cliente.nombre, cliente.apellido_paterno, cliente.apellido_materno, cliente.telefono, cliente.email)
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
            clientes.append(Cliente(id_cliente=fila[0], nombre=fila[1], apellido_paterno=fila[2], apellido_materno=fila[3], telefono=fila[4], email=fila[5]))
    except Error as e:
        print(f"Error al consultar clientes: {e}")
    finally:
        if cursor: cursor.close()
    return clientes

# --- Paquetes ---
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
        for f in cursor.fetchall():
            paquetes.append(Paquete(id_paquete=f[0], nombre=f[1], descripcion=f[2], precio=f[3]))
    except Error as e:
        print(f"Error al consultar paquetes: {e}")
    finally:
        if cursor: cursor.close()
    return paquetes

# --- Eventos y Catálogos ---
def get_metodos_pago_db(conexion):
    metodos = []
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_metodo, nombre_metodo FROM Metodos_Pago")
        for f in cursor.fetchall():
            metodos.append({"id": f[0], "nombre": f[1]})
    finally:
        if cursor: cursor.close()
    return metodos

def agregar_evento_db(conexion, evento):
    cursor = None
    try:
        cursor = conexion.cursor()
        # MODIFICADO: Agregamos id_usuario
        sql_evento = "INSERT INTO Eventos (id_cliente, id_usuario, fecha_evento, hora_evento, lugar, adelanto, id_metodo_pago) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        valores_evento = (evento.id_cliente, evento.id_usuario, evento.fecha_evento, evento.hora_evento, evento.lugar, evento.adelanto, evento.id_metodo_pago)
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
        SELECT e.id_evento, e.fecha_evento, e.lugar, CONCAT(c.nombre, ' ', c.apellido_paterno) as cliente,
               IFNULL(m.nombre_metodo, 'N/A') as metodo_pago, e.adelanto, IFNULL(SUM(ep.cantidad * p.precio), 0) as total_evento
        FROM Eventos e
        JOIN Clientes c ON e.id_cliente = c.id_cliente
        LEFT JOIN Metodos_Pago m ON e.id_metodo_pago = m.id_metodo
        LEFT JOIN Evento_Paquete ep ON e.id_evento = ep.id_evento
        LEFT JOIN Paquetes p ON ep.id_paquete = p.id_paquete
        GROUP BY e.id_evento ORDER BY e.fecha_evento DESC
        """
        cursor.execute(sql)
        for f in cursor.fetchall():
            eventos.append({"id": f[0], "fecha": f[1], "lugar": f[2], "cliente": f[3], "metodo_pago": f[4], "adelanto": f[5], "total": f[6]})
    finally:
        if cursor: cursor.close()
    return eventos

# --- Dashboard ---
def get_dashboard_stats(conexion):
    stats = {"total_clientes": 0, "total_eventos": 0, "ingresos_totales": 0.0}
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM Clientes")
        stats["total_clientes"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Eventos")
        stats["total_eventos"] = cursor.fetchone()[0]
        cursor.execute("SELECT IFNULL(SUM(ep.cantidad * p.precio), 0) FROM Evento_Paquete ep JOIN Paquetes p ON ep.id_paquete = p.id_paquete")
        stats["ingresos_totales"] = float(cursor.fetchone()[0])
    finally:
        if cursor: cursor.close()
    return stats

# =================================================================
# --- FUNCIONES DE EDICIÓN Y ELIMINACIÓN ---
# =================================================================

# --- ELIMINAR ---
def eliminar_evento_db(conexion, id_evento):
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM Eventos WHERE id_evento = %s", (id_evento,))
        conexion.commit()
    except Error as e:
        print(f"Error al eliminar evento: {e}")
    finally:
        cursor.close()

def eliminar_cliente_db(conexion, id_cliente):
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM Clientes WHERE id_cliente = %s", (id_cliente,))
        conexion.commit()
    except Error as e:
        print(f"Error: No se puede eliminar un cliente con eventos registrados.")
    finally:
        cursor.close()

def eliminar_paquete_db(conexion, id_paquete):
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM Paquetes WHERE id_paquete = %s", (id_paquete,))
        conexion.commit()
    except Error as e:
        print(f"Error: No se puede eliminar un paquete que ya fue vendido en un evento.")
    finally:
        cursor.close()

# --- EDITAR (LEER UN REGISTRO) ---
def get_paquete_por_id(conexion, id_paquete):
    cursor = conexion.cursor()
    cursor.execute("SELECT id_paquete, nombre_paquete, descripcion, precio FROM Paquetes WHERE id_paquete = %s", (id_paquete,))
    f = cursor.fetchone()
    cursor.close()
    if f: return Paquete(id_paquete=f[0], nombre=f[1], descripcion=f[2], precio=f[3])
    return None

def get_cliente_por_id(conexion, id_cliente):
    cursor = conexion.cursor()
    cursor.execute("SELECT id_cliente, nombre, apellido_paterno, apellido_materno, telefono, email FROM Clientes WHERE id_cliente = %s", (id_cliente,))
    f = cursor.fetchone()
    cursor.close()
    if f: return Cliente(id_cliente=f[0], nombre=f[1], apellido_paterno=f[2], apellido_materno=f[3], telefono=f[4], email=f[5])
    return None

# --- ACTUALIZAR ---
def actualizar_paquete_db(conexion, paquete):
    cursor = conexion.cursor()
    try:
        sql = "UPDATE Paquetes SET nombre_paquete=%s, descripcion=%s, precio=%s WHERE id_paquete=%s"
        cursor.execute(sql, (paquete.nombre_paquete, paquete.descripcion, paquete.precio, paquete.id_paquete))
        conexion.commit()
    except Error as e:
        print(f"Error al actualizar paquete: {e}")
    finally:
        cursor.close()

def actualizar_cliente_db(conexion, cliente):
    cursor = conexion.cursor()
    try:
        sql = "UPDATE Clientes SET nombre=%s, apellido_paterno=%s, apellido_materno=%s, telefono=%s, email=%s WHERE id_cliente=%s"
        cursor.execute(sql, (cliente.nombre, cliente.apellido_paterno, cliente.apellido_materno, cliente.telefono, cliente.email, cliente.id_cliente))
        conexion.commit()
    except Error as e:
        print(f"Error al actualizar cliente: {e}")
    finally:
        cursor.close()

