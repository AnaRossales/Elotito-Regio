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

def get_clientes_db(conexion, busqueda=None):
    clientes = []
    cursor = None
    try:
        cursor = conexion.cursor()
        
        # Si el usuario escribió algo en el buscador:
        if busqueda:
            sql = """
            SELECT id_cliente, nombre, apellido_paterno, apellido_materno, telefono, email 
            FROM clientes 
            WHERE nombre LIKE %s OR apellido_paterno LIKE %s OR telefono LIKE %s OR email LIKE %s
            """
            filtro = f"%{busqueda}%"
            cursor.execute(sql, (filtro, filtro, filtro, filtro))
        else:
            # Si no hay búsqueda, traemos todos
            cursor.execute("SELECT id_cliente, nombre, apellido_paterno, apellido_materno, telefono, email FROM clientes")
            
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

def get_eventos_db(conexion, busqueda=None):
    eventos = []
    cursor = None
    try:
        cursor = conexion.cursor()
        sql = """
        SELECT e.id_evento, e.fecha_evento, e.lugar, CONCAT(c.nombre, ' ', c.apellido_paterno) as cliente,
               IFNULL(m.nombre_metodo, 'N/A') as metodo_pago, e.adelanto, IFNULL(SUM(ep.cantidad * p.precio), 0) as total_evento
        FROM eventos e
        JOIN clientes c ON e.id_cliente = c.id_cliente
        LEFT JOIN metodos_pago m ON e.id_metodo_pago = m.id_metodo
        LEFT JOIN evento_paquete ep ON e.id_evento = ep.id_evento
        LEFT JOIN paquetes p ON ep.id_paquete = p.id_paquete
        """
        
        # Si hay búsqueda, filtramos por cliente, lugar o fecha
        if busqueda:
            sql += " WHERE CONCAT(c.nombre, ' ', c.apellido_paterno) LIKE %s OR e.lugar LIKE %s OR e.fecha_evento LIKE %s "
            
        sql += " GROUP BY e.id_evento ORDER BY e.fecha_evento DESC "
        
        if busqueda:
            filtro = f"%{busqueda}%"
            cursor.execute(sql, (filtro, filtro, filtro))
        else:
            cursor.execute(sql)
            
        for f in cursor.fetchall():
            fecha_formateada = f[1].strftime('%d/%m/%Y') if hasattr(f[1], 'strftime') else f[1]
            eventos.append({"id": f[0], "fecha": fecha_formateada, "lugar": f[2], "cliente": f[3], "metodo_pago": f[4], "adelanto": f[5], "total": f[6]})
    finally:
        if cursor: cursor.close()
    return eventos

# ¡NUEVA FUNCIÓN! Busca el evento más cercano a la fecha de hoy
def get_proximo_evento(conexion):
    cursor = None
    try:
        cursor = conexion.cursor()
        sql = """
        SELECT e.id_evento, e.fecha_evento, e.hora_evento, e.lugar, CONCAT(c.nombre, ' ', c.apellido_paterno) as cliente
        FROM eventos e
        JOIN clientes c ON e.id_cliente = c.id_cliente
        WHERE e.fecha_evento >= CURDATE()
        ORDER BY e.fecha_evento ASC, e.hora_evento ASC
        LIMIT 1
        """
        cursor.execute(sql)
        f = cursor.fetchone()
        if f:
            return {
                "id": f[0], 
                "fecha": f[1].strftime('%d/%m/%Y') if hasattr(f[1], 'strftime') else f[1],
                "hora": str(f[2])[:5], # Toma solo HH:MM
                "lugar": f[3],
                "cliente": f[4]
            }
        return None
    except Exception as e:
        print(f"Error al obtener próximo evento: {e}")
        return None
    finally:
        if cursor: cursor.close()

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

def get_usuario_por_nombre(conexion, nombre_usuario):
    cursor = None
    try:
        # ESTA ES LA LÍNEA CRÍTICA: Añade dictionary=True
        cursor = conexion.cursor(dictionary=True) 
        
        cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
        usuario = cursor.fetchone()
        return usuario
    except Error as e:
        print(f"Error al consultar usuario: {e}")
        return None
    finally:
        if cursor: 
            cursor.close()
def get_dashboard_stats(conexion):

    stats = {"total_clientes": 0, "total_eventos": 0, "ingresos_totales": 0.0, "adelantos_totales": 0.0}
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM clientes")
        stats["total_clientes"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM eventos")
        stats["total_eventos"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT IFNULL(SUM(ep.cantidad * p.precio), 0) FROM evento_paquete ep JOIN paquetes p ON ep.id_paquete = p.id_paquete")
        stats["ingresos_totales"] = float(cursor.fetchone()[0])
        
        cursor.execute("SELECT IFNULL(SUM(adelanto), 0) FROM eventos")
        stats["adelantos_totales"] = float(cursor.fetchone()[0])
        
    finally:
        if cursor: cursor.close()
    return stats
def get_paquetes_db(conexion):
    cursor = conexion.cursor(dictionary=True)
    # Esta consulta agrupa los nombres y cantidades de los insumos en una sola cadena
    sql = """
        SELECT p.*, 
               GROUP_CONCAT(CONCAT('{"nombre":"', i.nombre_insumo, '","cantidad":', pi.cantidad_necesaria, '}') SEPARATOR ',') as insumos_info
        FROM paquetes p
        LEFT JOIN paquete_insumo pi ON p.id_paquete = pi.id_paquete
        LEFT JOIN insumos i ON pi.id_insumo = i.id_insumo
        GROUP BY p.id_paquete
    """
    cursor.execute(sql)
    paquetes = cursor.fetchall()
    
    # Formateamos para que el JavaScript lo entienda como una lista real
    for p in paquetes:
        p['insumos_json'] = f"[{p['insumos_info']}]" if p['insumos_info'] else "[]"
        
    cursor.close()
    return paquetes
def abonar_evento_db(conexion, id_evento, monto):
    cursor = None
    try:
        cursor = conexion.cursor()
        # Sumamos el monto recibido al valor actual del adelanto
        sql = "UPDATE eventos SET adelanto = adelanto + %s WHERE id_evento = %s"
        cursor.execute(sql, (monto, id_evento))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al registrar abono: {e}")
        return False
    finally:
        if cursor: cursor.close()

def get_evento_por_id(conexion, id_evento):
    cursor = conexion.cursor(dictionary=True)
    try:
        query = "SELECT * FROM eventos WHERE id_evento = %s"
        cursor.execute(query, (id_evento,))
        evento = cursor.fetchone()
        
        if evento:
            query_paquetes = """
                SELECT id_paquete, cantidad 
                FROM evento_paquete 
                WHERE id_evento = %s
            """
            cursor.execute(query_paquetes, (id_evento,))
            evento['paquetes_seleccionados'] = cursor.fetchall()
            
        return evento
    except Exception as e:
        print(f"Error en get_evento_por_id: {e}")
        return None
    finally:
        if cursor: cursor.close()

def actualizar_evento_completo_db(conexion, id_evento, datos, paquetes):
    cursor = conexion.cursor()
    try:
        # 1. Actualizar datos básicos
        sql_base = "UPDATE eventos SET id_cliente=%s, fecha_evento=%s, hora_evento=%s, lugar=%s WHERE id_evento=%s"
        cursor.execute(sql_base, (datos['id_cliente'], datos['fecha'], datos['hora'], datos['lugar'], id_evento))
        
        # 2. Borrar paquetes anteriores para no duplicar
        cursor.execute("DELETE FROM evento_paquete WHERE id_evento = %s", (id_evento,))
        
        # 3. Insertar los nuevos seleccionados
        sql_p = "INSERT INTO evento_paquete (id_evento, id_paquete, cantidad) VALUES (%s, %s, %s)"
        for id_p, cant in paquetes:
            if cant > 0:
                cursor.execute(sql_p, (id_evento, id_p, cant))
        
        conexion.commit()
    finally:
        cursor.close()        

def get_insumos_db(conexion):
    cursor = conexion.cursor(dictionary=True)
    # Seleccionamos los nombres exactos de tu script SQL
    query = "SELECT id_insumo, nombre_insumo, costo_unitario, unidad_medida FROM insumos"
    cursor.execute(query)
    insumos = cursor.fetchall()
    cursor.close()
    return insumos

def update_paquete(id_paquete, nombre, precio, descripcion):
    conexion = crear_conexion()# Asegúrate de que así se llame tu función de conexión
    try:
        with conexion.cursor() as cursor:
            sql = """
                UPDATE paquetes 
                SET nombre_paquete = %s, 
                    precio = %s, 
                    descripcion = %s 
                WHERE id_paquete = %s
            """
            cursor.execute(sql, (nombre, precio, descripcion, id_paquete))
            conexion.commit()
            print(f"Paquete {id_paquete} actualizado correctamente.")
    except Exception as e:
        print(f"Error al actualizar paquete: {e}")
    finally:
        conexion.close()


# --- FUNCIONES PARA PROVEEDORES ---

def obtener_proveedores():
    conexion = crear_conexion()
    proveedores = []
    try:
        # Intentamos usar dictionary=True para que funcione p.nombre_contacto
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id_proveedor, contacto_nombre, razon_social, rfc, telefono, email FROM proveedores")
            proveedores = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener proveedores: {e}")
        # Si falla el diccionario, lo intentamos normal y lo convertimos a mano
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_proveedor, contacto_nombre, razon_social, rfc, telefono, email FROM proveedores")
            columnas = [col[0] for col in cursor.description]
            proveedores = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    finally:
        conexion.close()
    return proveedores

def insertar_proveedor(nombre, razon, rfc, tel, email):
    conexion = crear_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = """INSERT INTO proveedores (contacto_nombre, razon_social, rfc, telefono, email) 
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (nombre, razon, rfc, tel, email))
            conexion.commit()
    except Exception as e:
        print(f"Error al insertar proveedor: {e}")
    finally:
        conexion.close()

def update_proveedor(id_p, nombre, razon, rfc, tel, email):
    conexion = crear_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = """UPDATE proveedores 
                     SET contacto_nombre=%s, razon_social=%s, rfc=%s, telefono=%s, email=%s 
                     WHERE id_proveedor=%s"""
            cursor.execute(sql, (nombre, razon, rfc, tel, email, id_p))
            conexion.commit()
    except Exception as e:
        print(f"Error al actualizar proveedor: {e}")
    finally:
        conexion.close()

def borrar_proveedor(id_p):
    conexion = crear_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM proveedores WHERE id_proveedor = %s", (id_p,))
            conexion.commit()
    except Exception as e:
        print(f"Error al borrar proveedor: {e}")
    finally:
        conexion.close()

def update_proveedor(id_p, nombre_empresa, contacto_nombre, razon, rfc, tel, email):
    conexion = crear_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = """UPDATE proveedores 
                     SET nombre_empresa=%s, contacto_nombre=%s, razon_social=%s, rfc=%s, telefono=%s, email=%s 
                     WHERE id_proveedor=%s"""
            cursor.execute(sql, (nombre_empresa, contacto_nombre, razon, rfc, tel, email, id_p))
            conexion.commit()
    except Exception as e:
        print(f"Error al actualizar proveedor: {e}")
    finally:
        conexion.close()

def borrar_proveedor(id_p):
    conexion = crear_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM proveedores WHERE id_proveedor = %s", (id_p,))
            conexion.commit()
    except Exception as e:
        print(f"Error al borrar proveedor: {e}")
    finally:
        conexion.close()

# ==========================================
# FUNCIONES DE INSUMOS
# ==========================================

def obtener_insumos_completos():
    conexion = crear_conexion()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            # Hacemos JOIN para traer los datos del proveedor si es que tiene uno asignado
            sql = """
                SELECT i.*, p.nombre_empresa, p.contacto_nombre 
                FROM insumos i 
                LEFT JOIN proveedores p ON i.id_proveedor = p.id_proveedor
                ORDER BY i.nombre_insumo ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener insumos: {e}")
        return []
    finally:
        conexion.close()

def insertar_insumo(nombre, costo, unidad, prov_id):
    conexion = crear_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "INSERT INTO insumos (nombre_insumo, costo_unitario, unidad_medida, id_proveedor) VALUES (%s, %s, %s, %s)"
            # Si prov_id viene vacío del formulario, mandamos None para que SQL guarde NULL
            val_prov = prov_id if prov_id and str(prov_id).strip() != "" else None
            cursor.execute(sql, (nombre, costo, unidad, val_prov))
            conexion.commit()
    except Exception as e:
        print(f"Error al insertar insumo: {e}")
    finally:
        conexion.close()

def update_insumo(id_insumo, nombre, costo, unidad, prov_id):
    conexion = crear_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "UPDATE insumos SET nombre_insumo=%s, costo_unitario=%s, unidad_medida=%s, id_proveedor=%s WHERE id_insumo=%s"
            val_prov = prov_id if prov_id and str(prov_id).strip() != "" else None
            cursor.execute(sql, (nombre, costo, unidad, val_prov, id_insumo))
            conexion.commit()
    except Exception as e:
        print(f"Error al actualizar insumo: {e}")
    finally:
        conexion.close()

def borrar_insumo(id_insumo):
    conexion = crear_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM insumos WHERE id_insumo = %s", (id_insumo,))
            conexion.commit()
    except Exception as e:
        print(f"Error al borrar insumo: {e}")
    finally:
        conexion.close()
def guardar_paquete_con_insumos(conexion, nombre, descripcion, precio, insumos_seleccionados):
    cursor = conexion.cursor()
    try:
        # 1. Insertar el paquete
        sql_paquete = "INSERT INTO paquetes (nombre_paquete, descripcion, precio) VALUES (%s, %s, %s)"
        cursor.execute(sql_paquete, (nombre, descripcion, precio))
        id_nuevo_paquete = cursor.lastrowid

        # 2. Insertar la relación de insumos (la tabla pivote que creaste)
        sql_pivote = "INSERT INTO paquete_insumo (id_paquete, id_insumo, cantidad_necesaria) VALUES (%s, %s, %s)"
        for item in insumos_seleccionados:
            # item es una tupla (id_insumo, cantidad)
            cursor.execute(sql_pivote, (id_nuevo_paquete, item[0], item[1]))
        
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al guardar paquete e insumos: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()