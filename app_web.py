from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db_manager
from models.cliente import Cliente
from models.paquete import Paquete
from models.evento import Evento

app = Flask(__name__)
app.secret_key = 'elotito_regio_secreto_12345' 
conexion_db = db_manager.crear_conexion()

# =================================================================
# --- ZONA PÚBLICA ---
# =================================================================
@app.route('/')
def index_publico():
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
    
    lista_paquetes = db_manager.get_paquetes_db(conexion_db)
    return render_template('publico.html', paquetes=lista_paquetes)

# =================================================================
# --- SISTEMA DE LOGIN ---
# =================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        if usuario == 'admin' and password == 'elote123':
            session['admin_logueado'] = True
            return redirect(url_for('dashboard_admin'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logueado', None)
    return redirect(url_for('index_publico'))

def requiere_login():
    return 'admin_logueado' not in session

# =================================================================
# --- ZONA PRIVADA (DASHBOARD) ---
# =================================================================
@app.route('/admin')
def dashboard_admin():
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        
    stats = db_manager.get_dashboard_stats(conexion_db)
    ultimos_eventos = db_manager.get_eventos_db(conexion_db)[:5] 
    return render_template('dashboard.html', stats=stats, ultimos_eventos=ultimos_eventos)

# =================================================================
# --- MÓDULO DE EVENTOS ---
# =================================================================
@app.route('/registrar_evento')
def pagina_registrar_evento():
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        
    return render_template('registrar_evento.html', 
                           lista_clientes=db_manager.get_clientes_db(conexion_db), 
                           lista_paquetes=db_manager.get_paquetes_db(conexion_db),
                           lista_metodos=db_manager.get_metodos_pago_db(conexion_db))

@app.route('/guardar_evento', methods=['POST'])
def guardar_evento():
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
    
    id_metodo = request.form.get('id_metodo_pago')
    id_metodo = int(id_metodo) if id_metodo else None

    nuevo_evento = Evento(
        id_cliente=int(request.form['id_cliente']),
        fecha_evento=request.form['fecha_evento'],
        hora_evento=request.form['hora_evento'],
        lugar=request.form['lugar'],
        adelanto=float(request.form.get('adelanto') or 0.0),
        id_metodo_pago=id_metodo
    )
    
    for id_paquete_str in request.form.getlist('paquetes_seleccionados'):
        cantidad_str = request.form.get(f'cantidad_{id_paquete_str}')
        if cantidad_str and int(cantidad_str) > 0:
            nuevo_evento.agregar_paquete(int(id_paquete_str), int(cantidad_str))
            
    db_manager.agregar_evento_db(conexion_db, nuevo_evento)
    return redirect(url_for('pagina_eventos_lista'))

@app.route('/eventos_lista')
def pagina_eventos_lista():
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
    return render_template('eventos_lista.html', lista_eventos=db_manager.get_eventos_db(conexion_db))

@app.route('/eliminar_evento/<int:id>')
def eliminar_evento(id):
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected(): conexion_db = db_manager.crear_conexion()
    db_manager.eliminar_evento_db(conexion_db, id)
    return redirect(url_for('pagina_eventos_lista'))

# =================================================================
# --- MÓDULO DE CLIENTES ---
# =================================================================
@app.route('/clientes')
def pagina_clientes():
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected(): conexion_db = db_manager.crear_conexion()
    return render_template('clientes.html', lista_clientes=db_manager.get_clientes_db(conexion_db))

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected(): conexion_db = db_manager.crear_conexion()
    
    nuevo_cliente = Cliente(
        nombre=request.form['nombre'],
        apellido_paterno=request.form['apellido_paterno'],
        apellido_materno=request.form.get('apellido_materno', ''), 
        telefono=request.form.get('telefono', ''),
        email=request.form.get('email', '')
    )
    db_manager.agregar_cliente_db(conexion_db, nuevo_cliente)
    return redirect(url_for('pagina_clientes'))

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected(): conexion_db = db_manager.crear_conexion()
    
    if request.method == 'POST':
        cliente_actualizado = Cliente(
            id_cliente=id,
            nombre=request.form['nombre'],
            apellido_paterno=request.form['apellido_paterno'],
            apellido_materno=request.form.get('apellido_materno', ''),
            telefono=request.form.get('telefono', ''),
            email=request.form.get('email', '')
        )
        db_manager.actualizar_cliente_db(conexion_db, cliente_actualizado)
        return redirect(url_for('pagina_clientes'))
    
    cliente_a_editar = db_manager.get_cliente_por_id(conexion_db, id)
    return render_template('clientes.html', lista_clientes=db_manager.get_clientes_db(conexion_db), cliente_editar=cliente_a_editar)

@app.route('/eliminar_cliente/<int:id>')
def eliminar_cliente(id):
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected(): conexion_db = db_manager.crear_conexion()
    db_manager.eliminar_cliente_db(conexion_db, id)
    return redirect(url_for('pagina_clientes'))

# =================================================================
# --- MÓDULO DE PAQUETES ---
# =================================================================
@app.route('/paquetes')
def pagina_paquetes():
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected(): conexion_db = db_manager.crear_conexion()
    return render_template('paquetes.html', lista_paquetes=db_manager.get_paquetes_db(conexion_db))

@app.route('/guardar_paquete', methods=['POST'])
def guardar_paquete():
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected(): conexion_db = db_manager.crear_conexion()
    
    nuevo_paquete = Paquete(
        nombre=request.form['nombre_paquete'],
        descripcion=request.form.get('descripcion', ''),
        precio=float(request.form['precio'])
    )
    db_manager.agregar_paquete_db(conexion_db, nuevo_paquete)
    return redirect(url_for('pagina_paquetes'))

@app.route('/editar_paquete/<int:id>', methods=['GET', 'POST'])
def editar_paquete(id):
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected(): conexion_db = db_manager.crear_conexion()
    
    if request.method == 'POST':
        paquete_actualizado = Paquete(
            id_paquete=id,
            nombre=request.form['nombre_paquete'],
            descripcion=request.form.get('descripcion', ''),
            precio=float(request.form['precio'])
        )
        db_manager.actualizar_paquete_db(conexion_db, paquete_actualizado)
        return redirect(url_for('pagina_paquetes'))
    
    paquete_a_editar = db_manager.get_paquete_por_id(conexion_db, id)
    return render_template('paquetes.html', lista_paquetes=db_manager.get_paquetes_db(conexion_db), paquete_editar=paquete_a_editar)

@app.route('/eliminar_paquete/<int:id>')
def eliminar_paquete(id):
    if requiere_login(): return redirect(url_for('login'))
    global conexion_db
    if not conexion_db or not conexion_db.is_connected(): conexion_db = db_manager.crear_conexion()
    db_manager.eliminar_paquete_db(conexion_db, id)
    return redirect(url_for('pagina_paquetes'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)