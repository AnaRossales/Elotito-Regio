# models/cliente.py
# Define la clase Cliente, que solo guarda los datos.

class Cliente:
    def __init__(self, nombre, telefono, email, direccion, id_cliente=None, fecha_registro=None):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.fecha_registro = fecha_registro

    def __str__(self):
        """Devuelve una representación en texto del cliente."""
        return f"ID: {self.id_cliente} | Nombre: {self.nombre} | Tel: {self.telefono}"