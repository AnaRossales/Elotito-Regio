from database import db_manager

conexion = db_manager.crear_conexion()
if conexion and conexion.is_connected():
    print("✅ ¡Conexión exitosa! El sistema y la base de datos se hablan perfectamente.")
    conexion.close()
else:
    print("❌ No se pudo conectar. Verifica que MySQL esté encendido en XAMPP.")