# ui/menu.py
# Contiene todas las funciones de interfaz de usuario (menús de consola).

from database import db_manager
from models.cliente import Cliente
from models.paquete import Paquete
from models.evento import Evento
import datetime

# --- Funciones de ayuda (Helpers) ---

def mostrar_clientes(conexion):
    """Obtiene y muestra una lista de clientes. Devuelve la lista."""
    print("\n--- Listado de Clientes ---")
    lista_clientes = db_manager.get_clientes_db(conexion)
    if not lista_clientes:
        print("No hay clientes registrados.")
        return []
    for cliente in lista_clientes:
        print(str(cliente))
    return lista_clientes

def mostrar_paquetes(conexion):
    """Obtiene y muestra una lista de paquetes. Devuelve la lista."""
    print("\n--- Listado de Paquetes ---")
    lista_paquetes = db_manager.get_paquetes_db(conexion)
    if not lista_paquetes:
        print("No hay paquetes registrados.")
        return []
    for paquete in lista_paquetes:
        print(str(paquete))
    return lista_paquetes

# --- Funciones UI (Acciones del Menú) ---

def registrar_cliente_ui(conexion):
    """Pide los datos del cliente al usuario y lo registra."""
    print("\n--- Registro de Nuevo Cliente ---")
    nombre = input("Nombre completo: ")
    telefono = input("Teléfono: ")
    email = input("Email: ")
    direccion = input("Dirección: ")
    
    nuevo_cliente = Cliente(
        nombre=nombre, telefono=telefono, email=email,
        direccion=direccion, fecha_registro=datetime.date.today()
    )
    
    nuevo_id = db_manager.agregar_cliente_db(conexion, nuevo_cliente)
    if nuevo_id:
        print(f"\n¡Cliente '{nombre}' registrado exitosamente con el ID {nuevo_id}!")

def registrar_paquete_ui(conexion):
    """Pide los datos del paquete al usuario y lo registra."""
    print("\n--- Registro de Nuevo Paquete ---")
    nombre = input("Nombre del paquete: ")
    descripcion = input("Descripción: ")
    
    while True:
        try:
            precio = float(input("Precio (ej. 1500.00): "))
            break
        except ValueError:
            print("Error: Ingrese un precio válido (solo números).")

    nuevo_paquete = Paquete(nombre=nombre, descripcion=descripcion, precio=precio)
    
    nuevo_id = db_manager.agregar_paquete_db(conexion, nuevo_paquete)
    if nuevo_id:
        print(f"\n¡Paquete '{nombre}' registrado exitosamente con el ID {nuevo_id}!")

def registrar_evento_ui(conexion):
    """Flujo completo para registrar un evento, cliente y paquetes."""
    print("\n--- Registro de Nuevo Evento ---")
    
    # 1. Seleccionar Cliente
    clientes = mostrar_clientes(conexion)
    if not clientes:
        print("Debe registrar un cliente antes de crear un evento.")
        return
    
    id_cliente_seleccionado = None
    while id_cliente_seleccionado is None:
        try:
            id_input = int(input("Ingrese el ID del cliente para este evento: "))
            # Validar que el ID exista en la lista
            if any(c.id_cliente == id_input for c in clientes):
                id_cliente_seleccionado = id_input
            else:
                print("ID de cliente no válido. Intente de nuevo.")
        except ValueError:
            print("Error: Ingrese un ID numérico.")

    # 2. Pedir datos del Evento
    fecha_evento = input("Fecha del evento (YYYY-MM-DD): ")
    hora_evento = input("Hora del evento (HH:MM): ")
    lugar = input("Lugar del evento: ")
    
    try:
        total = float(input("Costo total del evento: "))
        adelanto = float(input("Adelanto (0 si no aplica): "))
    except ValueError:
        print("Error en montos. Se cancela el registro.")
        return
        
    metodo_pago = input("Método de pago del adelanto: ")
    
    # 3. Crear el objeto Evento (aún sin paquetes)
    nuevo_evento = Evento(
        id_cliente=id_cliente_seleccionado, fecha_evento=fecha_evento,
        hora_evento=hora_evento, lugar=lugar, total=total,
        adelanto=adelanto, metodo_pago=metodo_pago
    )

    # 4. Agregar Paquetes al Evento
    paquetes = mostrar_paquetes(conexion)
    if not paquetes:
        print("Advertencia: No hay paquetes registrados en el sistema.")
    
    while True:
        try:
            id_paquete_input = int(input("\nIngrese el ID del paquete a agregar (0 para terminar): "))
            if id_paquete_input == 0:
                break
            
            # Validar que el ID del paquete exista
            if not any(p.id_paquete == id_paquete_input for p in paquetes):
                print("ID de paquete no válido.")
                continue
                
            cantidad = int(input(f"Cantidad del paquete ID {id_paquete_input}: "))
            if cantidad <= 0:
                print("La cantidad debe ser mayor a 0.")
                continue
                
            # Agregar el paquete al objeto Evento
            nuevo_evento.agregar_paquete(id_paquete_input, cantidad)
            print(f"Paquete ID {id_paquete_input} agregado (x{cantidad}).")
            
        except ValueError:
            print("Error: Ingrese un ID numérico.")
    
    if not nuevo_evento.paquetes:
        print("Advertencia: No se agregaron paquetes al evento.")
        if input("¿Desea continuar de todos modos? (s/n): ").lower() != 's':
            print("Registro de evento cancelado.")
            return

    # 5. Guardar todo en la Base de Datos
    nuevo_id_evento = db_manager.agregar_evento_db(conexion, nuevo_evento)
    if nuevo_id_evento:
        print(f"\n¡Evento registrado exitosamente con el ID {nuevo_id_evento}!")
    else:
        print("\nError: No se pudo registrar el evento.")

def ver_eventos_ui(conexion):
    """Muestra un listado simple de los próximos eventos."""
    print("\n--- Listado de Eventos Registrados ---")
    lista_eventos = db_manager.get_eventos_db(conexion)
    
    if not lista_eventos:
        print("No hay eventos registrados.")
        return

    for evento in lista_eventos:
        print(f"ID: {evento['id']} | Fecha: {evento['fecha']} | Cliente: {evento['cliente']} | Lugar: {evento['lugar']}")

# --- Menú Principal ---

def menu_principal():
    """Muestra el menú principal y maneja la lógica de la aplicación."""
    
    conexion = db_manager.crear_conexion()
    if not conexion:
        print("FATAL: No se pudo conectar a la base de datos. El programa terminará.")
        return

    print("¡Bienvenido al Sistema SAKALA para Elotito Regio!")

    while True:
        print("\n" + "="*40)
        print("         MENÚ PRINCIPAL SAKALA")
        print("="*40)
        print(" 1. Registrar Cliente")
        print(" 2. Ver Clientes")
        print(" 3. Registrar Paquete")
        print(" 4. Ver Paquetes")
        print(" 5. Registrar Evento")
        print(" 6. Ver Eventos")
        print(" 7. Salir")
        print("="*40)
        
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            registrar_cliente_ui(conexion)
        elif opcion == '2':
            mostrar_clientes(conexion)
        elif opcion == '3':
            registrar_paquete_ui(conexion)
        elif opcion == '4':
            mostrar_paquetes(conexion)
        elif opcion == '5':
            registrar_evento_ui(conexion)
        elif opcion == '6':
            ver_eventos_ui(conexion)
        elif opcion == '7':
            print("Saliendo del sistema... ¡Adiós!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")
            
    if conexion.is_connected():
        conexion.close()
        print("Conexión cerrada.")