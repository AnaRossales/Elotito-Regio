from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db_manager
from models.cliente import Cliente
from werkzeug.security import check_password_hash
from models.paquete import Paquete
from models.evento import Evento
from flask import abort

app = Flask(__name__)
app.secret_key = 'elotito_regio_secreto_12345' 
conexion_db = db_manager.crear_conexion()

# ────────────── ୨୧ ────────────────
# ═══════ HELPERS Y SEGURIDAD ═══════
# ────────────── ୨୧ ────────────────

def verificar_conexion():
    global conexion_db
    if not conexion_db or not conexion_db.is_connected():
        conexion_db = db_manager.crear_conexion()
        if conexion_db is None:
            abort(500, description="No pudimos enlazar con la base de datos de Elotito Regio.")
    return conexion_db

def requiere_login():
    return 'admin_logueado' not in session

def requiere_admin():
    """Retorna True si el usuario NO es administrador (bloqueo)"""
    if 'usuario_id' not in session:
        return True
    return not session.get('es_admin', False)

# ────────────── ୨୧ ────────────────
# ═══════ ZONA PÚBLICA ═══════
# ────────────── ୨୧ ────────────────

@app.route('/')
def index_publico():
    con = verificar_conexion()
    lista_paquetes = db_manager.get_paquetes_db(con)
    return render_template('publico.html', paquetes=lista_paquetes)

# ────────────── ୨୧ ────────────────
# ═══════ SISTEMA DE LOGIN ═══════
# ────────────── ୨୧ ────────────────

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
            session['es_admin'] = bool(usuario_db['es_admin']) 
            return redirect(url_for('dashboard_admin'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index_publico'))

# ────────────── ୨୧ ────────────────
# ═══════ DASHBOARD ═══════
# ────────────── ୨୧ ────────────────

@app.route('/admin')
def dashboard_admin():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    stats = db_manager.get_dashboard_stats(con)
    ultimos_eventos = db_manager.get_eventos_db(con)[:5] 
    proximo = db_manager.get_proximo_evento(con) 
    return render_template('dashboard.html', stats=stats, ultimos_eventos=ultimos_eventos, proximo_evento=proximo)

# ────────────── ୨୧ ────────────────
# ═══════ EVENTOS (VENTAS) ═══════
# ────────────── ୨୧ ────────────────

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

@app.route('/abonar_pago/<int:id_evento>/<monto>')
def abonar_pago(id_evento, monto):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()

    try:
        abono_seguro = max(0.01, float(monto)) 
        db_manager.abonar_evento_db(con, id_evento, abono_seguro)
        flash(f"Abono de ${abono_seguro:.2f} registrado correctamente.", "success")
        
    except ValueError:
        flash("El monto ingresado no es válido.", "danger")
    except Exception as e:
        print(f"Error al registrar abono: {e}")
        flash("Hubo un error al procesar el pago.", "danger")
        
    return redirect(url_for('eventos_lista'))
    

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

# ────────────── ୨୧ ────────────────
# ═══════ CLIENTES ═══════
# ────────────── ୨୧ ────────────────

@app.route('/clientes')
def pagina_clientes():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    termino_busqueda = request.args.get('q', '')
    lista = db_manager.get_clientes_db(con, termino_busqueda)
    return render_template('clientes.html', lista_clientes=lista, busqueda_actual=termino_busqueda)

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    
    nuevo_c = Cliente(
        nombre=request.form.get('nombre'),
        apellido_paterno=request.form.get('apellido_paterno'),
        apellido_materno=request.form.get('apellido_materno') or None, # NULL controlado si viaja vacío
        telefono=request.form.get('telefono') or None,
        email=request.form.get('email') or None
    )
    db_manager.agregar_cliente_db(con, nuevo_c)
    flash("Cliente guardado exitosamente.", "success")
    return redirect(url_for('pagina_clientes'))

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    
    if request.method == 'POST':
        cliente_actualizado = Cliente(
            id_cliente=id,
            nombre=request.form.get('nombre'),
            apellido_paterno=request.form.get('apellido_paterno'),
            apellido_materno=request.form.get('apellido_materno') or None,
            telefono=request.form.get('telefono') or None,
            email=request.form.get('email') or None
        )
        db_manager.actualizar_cliente_db(con, cliente_actualizado)
        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for('pagina_clientes'))
    
    cliente_a_editar = db_manager.get_cliente_por_id(con, id)
    lista = db_manager.get_clientes_db(con)
    return render_template('clientes.html', lista_clientes=lista, cliente_editar=cliente_a_editar, busqueda_actual='')

@app.route('/eliminar_cliente/<int:id>')
def eliminar_cliente(id):
    if requiere_login(): return redirect(url_for('login'))
    con = verificar_conexion()
    
    # Intentamos borrar y guardamos el resultado (True o False)
    se_pudo_borrar = db_manager.eliminar_cliente_db(con, id)
    
    if se_pudo_borrar:
        flash("Cliente eliminado del directorio.", "success")
    else:
        flash("No se puede eliminar: El cliente tiene eventos o pagos registrados.", "danger")
        
    return redirect(url_for('pagina_clientes'))

# ────────────── ୨୧ ────────────────
# ═══════ PAQUETES ═══════
# ────────────── ୨୧ ────────────────

@app.route('/paquetes')
def pagina_paquetes():
    if requiere_login(): return redirect(url_for('login'))
    if requiere_admin(): return redirect(url_for('dashboard_admin'))
    con = verificar_conexion()
    insumos = db_manager.get_insumos_db(con)
    paquetes = db_manager.get_paquetes_db(con)
    return render_template('paquetes.html', lista_paquetes=paquetes, lista_insumos=insumos)

@app.route('/guardar_paquete', methods=['POST'])
def guardar_paquete():
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    con = verificar_conexion()
    

    nombre = request.form['nombre_paquete']
    descripcion = request.form.get('descripcion', '')
    precio = max(0.0, float(request.form.get('precio', 0)))
    
    ids_insumos = request.form.getlist('insumos[]')
    cantidades_insumos = request.form.getlist('cantidades[]')
    
    lista_insumos = db_manager.get_insumos_db(con)
    costos_dict = {str(ins['id_insumo']): float(ins['costo_unitario']) for ins in lista_insumos}
    
    insumos_seleccionados = []
    costo_total = 0.0
    
    for id_ins, cant_str in zip(ids_insumos, cantidades_insumos):
            if id_ins and id_ins != "0" and cant_str:
                # La cantidad nunca bajará de 0
                cant = max(0.0, float(cant_str)) 
                if cant > 0:
                    costo_total += costos_dict.get(id_ins, 0.0) * cant
                    insumos_seleccionados.append((int(id_ins), cant))
            
    db_manager.guardar_paquete_con_insumos(con, nombre, descripcion, precio, insumos_seleccionados, costo_total)
    flash("Paquete y receta guardados exitosamente.", "success")
    return redirect(url_for('pagina_paquetes'))

@app.route('/eliminar_paquete/<int:id>')
def eliminar_paquete(id):
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    con = verificar_conexion()
    db_manager.eliminar_paquete_db(con, id)
    return redirect(url_for('pagina_paquetes'))

@app.route('/actualizar_paquete', methods=['POST'])
def actualizar_paquete():
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    con = verificar_conexion()
    
    id_paquete = request.form.get('id_paquete')
    nombre = request.form.get('nombre_paquete')
    precio = max(0.0, float(request.form.get('precio', 0)))
    desc = request.form.get('descripcion', '')
    
    ids_insumos = request.form.getlist('insumos[]')
    cantidades_insumos = request.form.getlist('cantidades[]')
    
    lista_insumos = db_manager.get_insumos_db(con)
    costos_dict = {str(ins['id_insumo']): float(ins['costo_unitario']) for ins in lista_insumos}
    
    insumos_seleccionados = []
    costo_total = 0.0


    for id_ins, cant_str in zip(ids_insumos, cantidades_insumos):
        if id_ins and id_ins != "0" and cant_str:
            # La cantidad nunca bajará de 0
            cant = max(0.0, float(cant_str)) 
            if cant > 0:
                costo_total += costos_dict.get(id_ins, 0.0) * cant
                insumos_seleccionados.append((int(id_ins), cant))
        db_manager.update_paquete(con, id_paquete, nombre, precio, desc, insumos_seleccionados, costo_total)
        flash("Paquete actualizado correctamente.", "success")
    return redirect(url_for('pagina_paquetes'))

# ────────────── ୨୧ ────────────────
# ═══════ PROVEEDORES ═══════
# ────────────── ୨୧ ────────────────

@app.route('/proveedores')
def proveedores_view():
    if requiere_login(): return redirect(url_for('login'))
    if requiere_admin(): return redirect(url_for('dashboard_admin'))
    lista = db_manager.obtener_proveedores()
    return render_template('proveedores.html', proveedores=lista)

@app.route('/guardar_proveedor', methods=['POST'])
def guardar_proveedor():
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    db_manager.insertar_proveedor(
        request.form.get('nombre_empresa'),
        request.form.get('contacto_nombre', ''),
        request.form.get('razon_social', ''),
        request.form.get('rfc', ''),
        request.form.get('telefono', ''),
        request.form.get('email', '')
    )
    return redirect('/proveedores')

@app.route('/actualizar_proveedor', methods=['POST'])
def actualizar_proveedor():
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    db_manager.update_proveedor(
        request.form.get('id_proveedor'),
        request.form.get('nombre_empresa'),
        request.form.get('contacto_nombre', ''),
        request.form.get('razon_social', ''),
        request.form.get('rfc', ''),
        request.form.get('telefono', ''),
        request.form.get('email', '')
    )
    return redirect('/proveedores')

@app.route('/eliminar_proveedor/<int:id>')
def eliminar_proveedor(id):
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    db_manager.borrar_proveedor(id)
    return redirect('/proveedores')

# ────────────── ୨୧ ────────────────
# ═══════ INSUMOS ═══════
# ────────────── ୨୧ ────────────────

@app.route('/insumos')
def insumos_view():
    if requiere_login(): return redirect(url_for('login'))
    if requiere_admin(): return redirect(url_for('dashboard_admin'))
    lista_insumos = db_manager.obtener_insumos_completos()
    lista_proveedores = db_manager.obtener_proveedores() 
    return render_template('insumos.html', insumos=lista_insumos, proveedores=lista_proveedores)

@app.route('/guardar_insumo', methods=['POST'])
def guardar_insumo():
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    db_manager.insertar_insumo(
        request.form.get('nombre_insumo'),
        request.form.get('costo_unitario'),
        request.form.get('id_unidad'), 
        request.form.get('id_proveedor')
    )
    return redirect('/insumos')

@app.route('/actualizar_insumo', methods=['POST'])
def actualizar_insumo():
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    db_manager.update_insumo(
        request.form.get('id_insumo'),
        request.form.get('nombre_insumo'),
        request.form.get('costo_unitario'),
        request.form.get('id_unidad'), 
        request.form.get('id_proveedor')
    )
    return redirect('/insumos')

@app.route('/eliminar_insumo/<int:id>')
def eliminar_insumo(id):
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    db_manager.borrar_insumo(id)
    return redirect('/insumos')

# ────────────── ୨୧ ────────────────
# ═══════ USUARIOS ═══════
# ────────────── ୨୧ ────────────────

@app.route('/usuarios')
def pagina_usuarios():
    if requiere_login(): return redirect(url_for('login'))
    if requiere_admin(): return redirect(url_for('dashboard_admin'))
    con = verificar_conexion()
    lista = db_manager.get_usuarios_db(con)
    return render_template('usuarios.html', lista_usuarios=lista, usuario_edit=None)

@app.route('/guardar_usuario', methods=['POST'])
def guardar_usuario():
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    con = verificar_conexion()
    
    es_admin = request.form.get('es_admin')
    id_rol = 1 if es_admin else 2 
    
    nombre_usuario = request.form.get('nombre_usuario')
    nombre = request.form.get('nombre')
    apellido_paterno = request.form.get('apellido_paterno')
    apellido_materno = request.form.get('apellido_materno') or None
    password = request.form.get('password')
    
    db_manager.agregar_usuario_db(
        con, 
        nombre_usuario, 
        nombre,         
        apellido_paterno,
        apellido_materno, 
        id_rol, 
        password
    )
    flash("Usuario guardado", "success")
    return redirect(url_for('pagina_usuarios'))

@app.route('/editar_usuario/<int:id>')
def editar_usuario(id):
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    con = verificar_conexion()
    u_edit = db_manager.obtener_usuario_por_id(con, id)
    return render_template('editar_usuario.html', usuario_edit=u_edit)

@app.route('/actualizar_usuario', methods=['POST'])
def actualizar_usuario():
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    con = verificar_conexion()
    
    es_admin = request.form.get('es_admin')
    id_rol = 1 if es_admin else 2
    
    db_manager.actualizar_usuario_db(
        con, 
        request.form.get('id_usuario'), 
        request.form.get('nombre_usuario'), 
        request.form.get('nombre'),         
        request.form.get('apellido_paterno'),       
        request.form.get('apellido_materno') or None, 
        id_rol, 
        request.form.get('password')
    )
    flash("Usuario actualizado", "success")
    return redirect(url_for('pagina_usuarios'))

@app.route('/eliminar_usuario/<int:id>')
def eliminar_usuario(id):
    if requiere_login() or requiere_admin(): return redirect(url_for('dashboard_admin'))
    if id == session.get('usuario_id'):
        flash("No puedes eliminar tu propio acceso", "error")
    else:
        con = verificar_conexion()
        db_manager.eliminar_usuario_db(con, id)
    return redirect(url_for('pagina_usuarios'))

# ────────────── ୨୧ ────────────────
# ═══════ MANEJO DE ERRORES ═══════
# ────────────── ୨୧ ────────────────

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('error_500.html', 
                           titulo="Error 404 - Página no encontrada", 
                           mensaje="La dirección web que ingresaste no existe o fue movida a otro lugar."), 404

@app.errorhandler(403)
def acceso_denegado(error):
    return render_template('error_500.html', 
                           titulo="Error 403 - Acceso Denegado", 
                           mensaje="No tienes los privilegios necesarios de Administrador para ver esta sección."), 403

@app.errorhandler(405)
def metodo_no_permitido(error):
    return render_template('error_500.html', 
                           titulo="Error 405 - Acción Bloqueada", 
                           mensaje="Intentaste acceder a una ruta de guardado directamente o recargaste un formulario ya enviado."), 405

@app.errorhandler(500)
def error_servidor(error):
    mensaje = error.description if hasattr(error, 'description') else "Error interno del servidor. La base de datos podría estar apagada."
    return render_template('error_500.html', 
                           titulo="Error 500 - Falla del Sistema", 
                           mensaje=mensaje), 500

@app.errorhandler(Exception)
def error_general(error):
    # Atrapa cualquier otro error "raro" de Python
    return render_template('error_500.html', 
                           titulo="¡Ups! Algo inesperado sucedió", 
                           mensaje="El sistema encontró un problema que no pudo resolver. Hemos registrado el error."), 500

# ────────────── ୨୧ ────────────────
# ═══════ ARRANQUE ═══════
# ────────────── ୨୧ ────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)