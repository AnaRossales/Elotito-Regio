# app_web.py
from flask import Flask, render_template, request, redirect, url_for, flash
from database import db_manager
from models.cliente import Cliente
from models.paquete import Paquete
from models.evento import Evento  # <-- ¡IMPORTANTE! AÑADIR ESTA LÍNEA
import datetime

app = Flask(__name__)
app.secret_key = 'tu_llave_secreta_puede_ser_cualquier_texto'
conexion_db = db_manager.crear_conexion()

# -----------------------------------------------------------------
# --- MÓDULO DE EVENTOS (El corazón del sistema) ---
# -----------------------------------------------------------------

@app.route('/')
def pagina_registrar_evento():
    """
    PÁGINA PRINCIPAL: Muestra el formulario para registrar un evento.
    Necesita cargar los clientes y paquetes para los menús desplegables.
    """
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de BD", 500
            
    # 1. Obtener clientes
    lista_clientes = db_manager.get_clientes_db(conexion_db)
    # 2. Obtener paquetes
    lista_paquetes = db_manager.get_paquetes_db(conexion_db)
    
    # 3. Enviar ambas listas al HTML
    return render_template('registrar_evento.html', 
                           lista_clientes=lista_clientes, 
                           lista_paquetes=lista_paquetes)

@app.route('/guardar_evento', methods=['POST'])
def guardar_evento():
    """
    Guarda el nuevo EVENTO, incluyendo sus paquetes, en la base de datos.
    Esta es la función más importante.
    """
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de BD", 500

    try:
        # 1. Crear el objeto Evento (con datos del form)
        nuevo_evento = Evento(
            id_cliente=request.form['id_cliente'],
            fecha_evento=request.form['fecha_evento'],
            hora_evento=request.form['hora_evento'],
            lugar=request.form['lugar'],
            total=float(request.form['total']),
            adelanto=float(request.form['adelanto']),
            metodo_pago=request.form['metodo_pago']
        )
        
        # 2. Obtener los paquetes seleccionados (los que tienen 'check')
        # Esto nos da una lista de IDs: ['1', '3', '5']
        paquetes_seleccionados_ids = request.form.getlist('paquetes_seleccionados')
        
        for id_paquete_str in paquetes_seleccionados_ids:
            # Para cada paquete con 'check', buscar su cantidad
            cantidad_str = request.form.get(f'cantidad_{id_paquete_str}')
            
            if cantidad_str and int(cantidad_str) > 0:
                # Añadir el paquete y su cantidad al objeto Evento
                nuevo_evento.agregar_paquete(int(id_paquete_str), int(cantidad_str))
                
        # 3. Guardar el evento y sus paquetes en la BD
        nuevo_id = db_manager.agregar_evento_db(conexion_db, nuevo_evento)
        
        if nuevo_id:
            print(f"¡Evento {nuevo_id} guardado!")
        else:
            print("Error al guardar evento.")

    except Exception as e:
        print(f"Error al procesar el evento: {e}")
        # Aquí podrías mostrar un mensaje de error al usuario
    
    # Redirigir a la lista de eventos para ver el resultado
    return redirect(url_for('pagina_eventos_lista'))

@app.route('/eventos_lista')
def pagina_eventos_lista():
    """Muestra el historial de eventos registrados."""
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de BD", 500
            
    # Obtenemos la lista de eventos desde la BD
    lista_eventos = db_manager.get_eventos_db(conexion_db)
    
    return render_template('eventos_lista.html', lista_eventos=lista_eventos)

# -----------------------------------------------------------------
# --- MÓDULO DE CLIENTES (Se queda casi igual) ---
# -----------------------------------------------------------------
@app.route('/clientes')
def pagina_clientes():
    return render_template('clientes.html')

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de BD", 500

    nombre_usuario = request.form['nombre']
    telefono_usuario = request.form['telefono']
    email_usuario = request.form['email']
    direccion_usuario = request.form['direccion']
    
    nuevo_cliente = Cliente(
        nombre=nombre_usuario, telefono=telefono_usuario,
        email=email_usuario, direccion=direccion_usuario,
        fecha_registro=datetime.date.today()
    )
    
    db_manager.agregar_cliente_db(conexion_db, nuevo_cliente)
    return redirect(url_for('pagina_clientes'))

# -----------------------------------------------------------------
# --- MÓDULO DE PAQUETES (Se queda casi igual) ---
# -----------------------------------------------------------------
@app.route('/paquetes')
def pagina_paquetes():
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de BD", 500
            
    lista_paquetes = db_manager.get_paquetes_db(conexion_db)
    return render_template('paquetes.html', lista_paquetes=lista_paquetes)

@app.route('/guardar_paquete', methods=['POST'])
def guardar_paquete():
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de BD", 500

    nombre = request.form['nombre_paquete']
    precio = request.form['precio']
    descripcion = request.form['descripcion']
    
    nuevo_paquete = Paquete(
        nombre=nombre,
        descripcion=descripcion,
        precio=float(precio)
    )
    
    db_manager.agregar_paquete_db(conexion_db, nuevo_paquete)
    return redirect(url_for('pagina_paquetes'))

# -----------------------------------------------------------------
# --- INICIO DE LA APP (Se queda igual) ---
# -----------------------------------------------------------------
if __name__ == '__main__':
    if not conexion_db:
        print("FATAL: No se pudo conectar a la base de datos de MySQL.")
        print("Asegúrate de que XAMPP esté corriendo (con MySQL encendido).")
    else:
        print("Conexión a MySQL exitosa.")
        app.run(debug=True, port=5000)