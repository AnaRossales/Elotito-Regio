-- 1. Crear la base de datos
CREATE DATABASE IF NOT EXISTS elotito_regio_db;
USE elotito_regio_db;

-- 2. Tabla de Clientes
CREATE TABLE IF NOT EXISTS Clientes (
    id_cliente INT(11) NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(15) NULL,
    email VARCHAR(100) NULL,
    direccion VARCHAR(150) NULL,
    fecha_registro DATE NOT NULL,
    PRIMARY KEY (id_cliente)
);

-- 3. Tabla de Paquetes
CREATE TABLE IF NOT EXISTS Paquetes (
    id_paquete INT(11) NOT NULL AUTO_INCREMENT,
    nombre_paquete VARCHAR(100) NOT NULL,
    descripcion TEXT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (id_paquete)
);

-- 4. Tabla de Eventos
CREATE TABLE IF NOT EXISTS Eventos (
    id_evento INT(11) NOT NULL AUTO_INCREMENT,
    id_cliente INT(11) NOT NULL,
    fecha_evento DATE NOT NULL,
    hora_evento TIME NOT NULL,
    lugar VARCHAR(150) NOT NULL,
    adelanto DECIMAL(10, 2) NULL DEFAULT 0.00,
    total DECIMAL(10, 2) NOT NULL,
    metodo_pago VARCHAR(50) NULL,
    PRIMARY KEY (id_evento),
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 5. Tabla de Detalle Evento-Paquete (Tabla de unión)
CREATE TABLE IF NOT EXISTS Evento_Paquete (
    id_evento_paquete INT(11) NOT NULL AUTO_INCREMENT,
    id_evento INT(11) NOT NULL,
    id_paquete INT(11) NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    PRIMARY KEY (id_evento_paquete),
    FOREIGN KEY (id_evento) REFERENCES Eventos(id_evento),
    FOREIGN KEY (id_paquete) REFERENCES Paquetes(id_paquete),
    UNIQUE KEY uk_evento_paquete (id_evento, id_paquete)
);