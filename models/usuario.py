class Usuario:
    def __init__(self, nombre_usuario, nombre, apellido_paterno, id_rol=2, es_admin=0, apellido_materno=None, telefono=None, id_usuario=None, password_hash=None):
        self.id_usuario = id_usuario
        self.id_rol = id_rol  
        self.nombre_usuario = nombre_usuario
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.telefono = telefono
        self.es_admin = es_admin 
        self.password_hash = password_hash