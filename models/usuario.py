class Usuario:
    def __init__(self, nombre_usuario, es_admin=0, id_usuario=None, password_hash=None):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.es_admin = es_admin
        self.password_hash = password_hash