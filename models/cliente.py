class Cliente:
    def __init__(self, nombre, apellido_paterno, apellido_materno, telefono, email, id_cliente=None):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.telefono = telefono
        self.email = email

    @property
    def nombre_completo(self):
        """Une los nombres y apellidos, ignorando el materno si está vacío"""
        if self.apellido_materno:
            return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
        return f"{self.nombre} {self.apellido_paterno}"

    def __str__(self):
        return f"ID: {self.id_cliente} | Nombre: {self.nombre_completo} | Tel: {self.telefono}"