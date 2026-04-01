# models/paquete.py
# Define la clase Paquete.

class Paquete:
    def __init__(self, nombre, descripcion, precio, id_paquete=None):
        self.id_paquete = id_paquete
        self.nombre_paquete = nombre
        self.descripcion = descripcion
        self.precio = precio

    def __str__(self):
        return f"ID: {self.id_paquete} | Paquete: {self.nombre_paquete} | Precio: ${self.precio:.2f}"