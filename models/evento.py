# models/evento.py
# Define la clase Evento.

class Evento:
    def __init__(self, id_cliente, fecha_evento, hora_evento, lugar, total, 
                 adelanto=0.0, metodo_pago="", id_evento=None):
        self.id_evento = id_evento
        self.id_cliente = id_cliente
        self.fecha_evento = fecha_evento
        self.hora_evento = hora_evento
        self.lugar = lugar
        self.total = total
        self.adelanto = adelanto
        self.metodo_pago = metodo_pago
        
        # Esta lista guardará tuplas de (id_paquete, cantidad)
        self.paquetes = [] 

    def agregar_paquete(self, id_paquete, cantidad):
        """Agrega un paquete (por ID) y su cantidad a la lista del evento."""
        self.paquetes.append((id_paquete, cantidad))
    
    def __str__(self):
        """Devuelve una representación simple del evento."""
        return (f"ID Evento: {self.id_evento} | Fecha: {self.fecha_evento} | "
                f"Cliente ID: {self.id_cliente} | Lugar: {self.lugar}")