from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db_manager
from models.cliente import Cliente
from werkzeug.security import check_password_hash
from models.paquete import Paquete
from models.evento import Evento

app = Flask(__name__)
app.secret_key = 'elotito_regio_secreto_12345' 
conexion_db = db_manager.crear_conexion()

# Helper para verificar conexión
def verificar_conexion():
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
    return conexion_db

def requiere_login():
    return 'admin_logueado' not in session

# =================================================================
# --- ZONA PÚBLICA ---
# =================================================================
@app.route('/')
def index_publico():
    con = verificar_conexion()
    lista_paquetes = db_manager.get_paquetes_db(con)
    return render_template('publico.html', paquetes=lista_paquetes)

# =================================================================
# --- SISTEMA DE LOGIN ---
# =================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_input = request.form.get('usuario')
        password_input = request.form.get('password')
        con = verificar_conexion()
        usuario_db = db_manager.get_usuario_por_nombre(con, usuario_input)
        
        if usuario_db and check_password_hash(usuario_db['password_hash'], password_input):
            session['admin_logueado'] = True
            session['usuario_id'] = usuario_db['id_usuario']
            session['nombre_usuario'] = usuario_db['nombre_usuario']
            session['es_admin'] = usuario_db['es_admin']
            return redirect(url_for('dashboard_admin'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logueado', None)
    return redirect(url_for('index_publico'))

# =================================================================
# --- ZONA PRIVADA (DASHBOARD) ---
# =================================================================
@app.route('/admin')
def dashboard_admin():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    stats = db_manager.get_dashboard_stats(con)
    ultimos_eventos = db_manager.get_eventos_db(con)[:5] 
    proximo = db_manager.get_proximo_evento(con) 
    return render_template('dashboard.html', stats=stats, ultimos_eventos=ultimos_eventos, proximo_evento=proximo)

# =================================================================
# --- MÓDULO DE EVENTOS ---
# =================================================================
@app.route('/registrar_evento')
def pagina_registrar_evento():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    return render_template('registrar_evento.html', 
                           lista_clientes=db_manager.get_clientes_db(con), 
                           lista_paquetes=db_manager.get_paquetes_db(con),
                           lista_metodos=db_manager.get_metodos_pago_db(con))

@app.route('/guardar_evento', methods=['POST'])
def guardar_evento():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    adelanto = float(request.form.get('adelanto') or 0.0)
    total_venta = 0.0
    paquetes_a_guardar = []

    for id_paquete_str in request.form.getlist('paquetes_seleccionados'):
        cantidad_str = request.form.get(f'cantidad_{id_paquete_str}')
        if cantidad_str and int(cantidad_str) > 0:
            id_paq = int(id_paquete_str)
            cant = int(cantidad_str)
            paquete_db = db_manager.get_paquete_por_id(con, id_paq)
            if paquete_db:
                total_venta += (float(paquete_db.precio) * cant)
            paquetes_a_guardar.append((id_paq, cant))

    if adelanto > total_venta:
        flash(f"Error: El adelanto (${adelanto}) no puede ser mayor al total (${total_venta}).", "error")
        return redirect(url_for('pagina_registrar_evento'))

    id_metodo = request.form.get('id_metodo_pago')
    id_metodo = int(id_metodo) if id_metodo else None

    nuevo_evento = Evento(
        id_cliente=int(request.form['id_cliente']),
        id_usuario=session.get('usuario_id'),
        fecha_evento=request.form['fecha_evento'],
        hora_evento=request.form['hora_evento'],
        lugar=request.form['lugar'],
        adelanto=adelanto,
        id_metodo_pago=id_metodo
    )
    for id_paquete, cantidad in paquetes_a_guardar:
        nuevo_evento.agregar_paquete(id_paquete, cantidad)
            
    db_manager.agregar_evento_db(con, nuevo_evento)
    return redirect(url_for('pagina_eventos_lista'))

@app.route('/eventos_lista')
def pagina_eventos_lista():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    termino_busqueda = request.args.get('q', '')
    lista = db_manager.get_eventos_db(con, termino_busqueda)
    return render_template('eventos_lista.html', lista_eventos=lista, busqueda_actual=termino_busqueda)

@app.route('/eliminar_evento/<int:id>')
def eliminar_evento(id):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    db_manager.eliminar_evento_db(con, id)
    return redirect(url_for('pagina_eventos_lista'))

@app.route('/abonar_pago/<int:id_evento>/<string:monto>')
def abonar_pago(id_evento, monto):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    try:
        monto_num = float(monto)
        if monto_num > 0:
            db_manager.abonar_evento_db(con, id_evento, monto_num)
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for('pagina_eventos_lista'))

@app.route('/editar_evento/<int:id>')
def editar_evento(id):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    evento = db_manager.get_evento_por_id(con, id) 
    clientes = db_manager.get_clientes_db(con)
    paquetes = db_manager.get_paquetes_db(con)
    return render_template('editar_evento.html', evento=evento, lista_clientes=clientes, lista_paquetes=paquetes)

@app.route('/actualizar_evento/<int:id>', methods=['POST'])
def actualizar_evento(id):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    datos = {
        'id_cliente': request.form['id_cliente'],
        'fecha': request.form['fecha_evento'],
        'hora': request.form['hora_evento'],
        'lugar': request.form['lugar']
    }
    paquetes = []
    for id_p in request.form.getlist('paquetes_seleccionados'):
        cant = request.form.get(f'cantidad_{id_p}', 0)
        paquetes.append((int(id_p), int(cant)))
    
    db_manager.actualizar_evento_completo_db(con, id, datos, paquetes)
    flash("Evento actualizado correctamente", "success")
    return redirect(url_for('pagina_eventos_lista'))

# =================================================================
# --- MÓDULO DE CLIENTES ---
# =================================================================
@app.route('/clientes')
def pagina_clientes():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    termino_busqueda = request.args.get('q', '')
    lista = db_manager.get_clientes_db(con, termino_busqueda)
    return render_template('clientes.html', lista_clientes=lista, busqueda_actual=termino_busqueda)

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    if request.method == 'POST':
        cliente_actualizado = Cliente(
            id_cliente=id,
            nombre=request.form['nombre'],
            apellido_paterno=request.form['apellido_paterno'],
            apellido_materno=request.form.get('apellido_materno', ''),
            telefono=request.form.get('telefono', ''),
            email=request.form.get('email', '')
        )
        db_manager.actualizar_cliente_db(con, cliente_actualizado)
        return redirect(url_for('pagina_clientes'))
    
    cliente_a_editar = db_manager.get_cliente_por_id(con, id)
    return render_template('clientes.html', lista_clientes=db_manager.get_clientes_db(con), cliente_editar=cliente_a_editar)

@app.route('/eliminar_cliente/<int:id>')
def eliminar_cliente(id):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    db_manager.eliminar_cliente_db(con, id)
    return redirect(url_for('pagina_clientes'))

# =================================================================
# --- MÓDULO DE PAQUETES ---
# =================================================================
@app.route('/paquetes')
def pagina_paquetes():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    insumos = db_manager.get_insumos_db(con)
    paquetes = db_manager.get_paquetes_db(con)
    return render_template('paquetes.html', lista_paquetes=paquetes, lista_insumos=insumos)

@app.route('/guardar_paquete', methods=['POST'])
def guardar_paquete():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    
    # Aquí puedes usar la función guardar_paquete_con_insumos si ya la tienes en db_manager
    # Por ahora dejo la lógica básica:
    nuevo_paquete = Paquete(
        nombre=request.form['nombre_paquete'],
        descripcion=request.form.get('descripcion', ''),
        precio=float(request.form['precio'])
    )
    db_manager.agregar_paquete_db(con, nuevo_paquete)
    return redirect(url_for('pagina_paquetes'))

@app.route('/eliminar_paquete/<int:id>')
def eliminar_paquete(id):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    db_manager.eliminar_paquete_db(con, id)
    return redirect(url_for('pagina_paquetes'))

# =================================================================
# --- ARRANQUE ---
# =================================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)