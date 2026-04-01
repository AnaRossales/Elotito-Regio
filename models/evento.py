class Evento:
    def __init__(self, id_cliente, fecha_evento, hora_evento, lugar, 
                 adelanto=0.0, id_metodo_pago=None, id_evento=None):
        self.id_evento = id_evento
        self.id_cliente = id_cliente
        self.fecha_evento = fecha_evento
        self.hora_evento = hora_evento
        self.lugar = lugar
        self.adelanto = adelanto
        self.id_metodo_pago = id_metodo_pago
        
        self.paquetes = [] 

    def agregar_paquete(self, id_paquete, cantidad):
        self.paquetes.append((id_paquete, cantidad))