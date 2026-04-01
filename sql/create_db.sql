-- 1. Crear la base de datos
CREATE DATABASE IF NOT EXISTS elotito_regio_db;
USE elotito_regio_db;

-- 2. Tabla de Clientes 
CREATE TABLE IF NOT EXISTS Clientes (
    id_cliente INT NOT NULL AUTO_INCREMENT, 
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NULL, 
    telefono VARCHAR(15) NULL,
    email VARCHAR(100) NULL,
    PRIMARY KEY (id_cliente)
);

-- 3. Tabla de Paquetes
CREATE TABLE IF NOT EXISTS Paquetes (
    id_paquete SMALLINT NOT NULL AUTO_INCREMENT, 
    nombre_paquete VARCHAR(100) NOT NULL,
    descripcion TEXT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (id_paquete)
);

-- 4. Catálogo de Métodos de Pago
CREATE TABLE IF NOT EXISTS Metodos_Pago (
    id_metodo TINYINT NOT NULL AUTO_INCREMENT, 
    nombre_metodo VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_metodo)
);

-- Insertar métodos de pago por defecto
INSERT INTO Metodos_Pago (nombre_metodo) VALUES 
('Efectivo'), ('Transferencia'), ('Tarjeta de Crédito/Débito');

-- 5. Tabla de Eventos 
CREATE TABLE IF NOT EXISTS Eventos (
    id_evento INT NOT NULL AUTO_INCREMENT, 
    id_cliente INT NOT NULL,
    fecha_evento DATE NOT NULL,
    hora_evento TIME NOT NULL,
    lugar VARCHAR(150) NOT NULL,
    adelanto DECIMAL(10, 2) NULL DEFAULT 0.00,
    id_metodo_pago TINYINT NULL, 
    PRIMARY KEY (id_evento),
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_metodo_pago) REFERENCES Metodos_Pago(id_metodo)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- 6. Tabla de Detalle Evento-Paquete 
CREATE TABLE IF NOT EXISTS Evento_Paquete (
    id_evento INT NOT NULL,
    id_paquete SMALLINT NOT NULL, 
    cantidad SMALLINT NOT NULL DEFAULT 1, 
    PRIMARY KEY (id_evento, id_paquete),
    FOREIGN KEY (id_evento) REFERENCES Eventos(id_evento)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_paquete) REFERENCES Paquetes(id_paquete)
        ON DELETE RESTRICT ON UPDATE CASCADE
);