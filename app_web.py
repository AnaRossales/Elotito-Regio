# app_web.py
from flask import Flask, render_template, request, redirect, url_for, flash
from database import db_manager
from models.cliente import Cliente
from models.paquete import Paquete
from models.evento import Evento

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
    Carga los clientes, paquetes y métodos de pago desde la BD.
    """
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de conexión a la Base de Datos", 500
            
    lista_clientes = db_manager.get_clientes_db(conexion_db)
    lista_paquetes = db_manager.get_paquetes_db(conexion_db)
    lista_metodos = db_manager.get_metodos_pago_db(conexion_db)
    
    return render_template('registrar_evento.html', 
                           lista_clientes=lista_clientes, 
                           lista_paquetes=lista_paquetes,
                           lista_metodos=lista_metodos)

@app.route('/guardar_evento', methods=['POST'])
def guardar_evento():
    """
    Guarda el nuevo EVENTO y sus paquetes en la base de datos.
    El total se calcula dinámicamente en la BD, por lo que no se guarda aquí.
    """
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de conexión a la Base de Datos", 500

    try:
        # 1. Obtener y validar el método de pago
        id_metodo_str = request.form.get('id_metodo_pago')
        id_metodo = int(id_metodo_str) if id_metodo_str else None

        # 2. Obtener y validar el adelanto
        adelanto_str = request.form.get('adelanto')
        adelanto = float(adelanto_str) if adelanto_str else 0.0

        # 3. Crear el objeto Evento (Sin el 'total' porque ahora es calculado)
        nuevo_evento = Evento(
            id_cliente=int(request.form['id_cliente']),
            fecha_evento=request.form['fecha_evento'],
            hora_evento=request.form['hora_evento'],
            lugar=request.form['lugar'],
            adelanto=adelanto,
            id_metodo_pago=id_metodo
        )
        
        # 4. Obtener los paquetes seleccionados (los checkboxes)
        paquetes_seleccionados_ids = request.form.getlist('paquetes_seleccionados')
        
        for id_paquete_str in paquetes_seleccionados_ids:
            # Buscar la cantidad ingresada para cada paquete seleccionado
            cantidad_str = request.form.get(f'cantidad_{id_paquete_str}')
            if cantidad_str and int(cantidad_str) > 0:
                nuevo_evento.agregar_paquete(int(id_paquete_str), int(cantidad_str))
                
        # 5. Guardar todo en la BD
        nuevo_id = db_manager.agregar_evento_db(conexion_db, nuevo_evento)
        
        if nuevo_id:
            print(f"¡Evento {nuevo_id} guardado exitosamente!")
        else:
            print("Error al guardar el evento en la BD.")

    except Exception as e:
        print(f"Error al procesar el evento: {e}")
    
    return redirect(url_for('pagina_eventos_lista'))

@app.route('/eventos_lista')
def pagina_eventos_lista():
    """Muestra el historial de eventos registrados."""
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de conexión a la Base de Datos", 500
            
    lista_eventos = db_manager.get_eventos_db(conexion_db)
    return render_template('eventos_lista.html', lista_eventos=lista_eventos)

# -----------------------------------------------------------------
# --- MÓDULO DE CLIENTES ---
# -----------------------------------------------------------------
@app.route('/clientes')
def pagina_clientes():
    return render_template('clientes.html')

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    """Guarda un cliente nuevo con la estructura de nombres separados."""
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de conexión a la Base de Datos", 500

    # apellido_materno, telefono y email usan .get() por si el usuario los deja vacíos
    nuevo_cliente = Cliente(
        nombre=request.form['nombre'],
        apellido_paterno=request.form['apellido_paterno'],
        apellido_materno=request.form.get('apellido_materno', ''), 
        telefono=request.form.get('telefono', ''),
        email=request.form.get('email', '')
    )
    
    db_manager.agregar_cliente_db(conexion_db, nuevo_cliente)
    return redirect(url_for('pagina_clientes'))

# -----------------------------------------------------------------
# --- MÓDULO DE PAQUETES ---
# -----------------------------------------------------------------
@app.route('/paquetes')
def pagina_paquetes():
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de conexión a la Base de Datos", 500
            
    lista_paquetes = db_manager.get_paquetes_db(conexion_db)
    return render_template('paquetes.html', lista_paquetes=lista_paquetes)

@app.route('/guardar_paquete', methods=['POST'])
def guardar_paquete():
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if not conexion_db:
            return "Error de conexión a la Base de Datos", 500

    nuevo_paquete = Paquete(
        nombre=request.form['nombre_paquete'],
        descripcion=request.form.get('descripcion', ''),
        precio=float(request.form['precio'])
    )
    
    db_manager.agregar_paquete_db(conexion_db, nuevo_paquete)
    return redirect(url_for('pagina_paquetes'))

# -----------------------------------------------------------------
# --- INICIO DE LA APP ---
# -----------------------------------------------------------------
if __name__ == '__main__':
    if not conexion_db:
        print("FATAL: No se pudo conectar a la base de datos de MySQL.")
        print("Asegúrate de que XAMPP esté corriendo y la BD esté creada.")
    else:
        print("Conexión a MySQL exitosa.")
        app.run(debug=True, port=5000)