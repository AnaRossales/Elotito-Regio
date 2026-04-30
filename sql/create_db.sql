-- =================================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS: ELOTITO REGIO
-- =================================================================

CREATE DATABASE IF NOT EXISTS elotito_regio_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE elotito_regio_db;

-- =================================================================
-- 1. TABLAS MAESTRAS (No dependen de otras tablas)
-- =================================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT NOT NULL AUTO_INCREMENT,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    es_admin TINYINT(1) DEFAULT 0,
    PRIMARY KEY (id_usuario)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) DEFAULT NULL,
    telefono VARCHAR(15) DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (id_cliente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS metodos_pago (
    id_metodo TINYINT NOT NULL AUTO_INCREMENT,
    nombre_metodo VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_metodo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT NOT NULL AUTO_INCREMENT,
    nombre_empresa VARCHAR(100) NOT NULL,
    contacto_nombre VARCHAR(100) DEFAULT NULL,
    telefono VARCHAR(15) DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (id_proveedor)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS paquetes (
    id_paquete SMALLINT NOT NULL AUTO_INCREMENT,
    nombre_paquete VARCHAR(100) NOT NULL,
    descripcion TEXT DEFAULT NULL,
    precio DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_paquete)
) ENGINE=InnoDB;

-- =================================================================
-- 2. TABLAS SECUNDARIAS (Dependen de las tablas maestras)
-- =================================================================

CREATE TABLE IF NOT EXISTS insumos (
    id_insumo INT NOT NULL AUTO_INCREMENT,
    nombre_insumo VARCHAR(100) NOT NULL,
    costo_unitario DECIMAL(10,2) NOT NULL,
    unidad_medida VARCHAR(20) DEFAULT NULL,
    id_proveedor INT DEFAULT NULL,
    PRIMARY KEY (id_insumo),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) 
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS eventos (
    id_evento INT NOT NULL AUTO_INCREMENT,
    id_cliente INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha_evento DATE NOT NULL,
    hora_evento TIME NOT NULL,
    lugar VARCHAR(150) NOT NULL,
    adelanto DECIMAL(10,2) DEFAULT 0.00,
    id_metodo_pago TINYINT DEFAULT NULL,
    PRIMARY KEY (id_evento),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_metodo_pago) REFERENCES metodos_pago(id_metodo) 
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- =================================================================
-- 3. TABLAS PIVOTE (Relaciones Muchos a Muchos)
-- =================================================================

CREATE TABLE IF NOT EXISTS paquete_insumo (
    id_paquete SMALLINT NOT NULL,
    id_insumo INT NOT NULL,
    cantidad_necesaria DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_paquete, id_insumo),
    FOREIGN KEY (id_paquete) REFERENCES paquetes(id_paquete) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo) 
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS evento_paquete (
    id_evento INT NOT NULL,
    id_paquete SMALLINT NOT NULL,
    cantidad SMALLINT NOT NULL DEFAULT 1,
    PRIMARY KEY (id_evento, id_paquete),
    FOREIGN KEY (id_evento) REFERENCES eventos(id_evento) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_paquete) REFERENCES paquetes(id_paquete) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =================================================================
-- 4. INSERCIÓN DE DATOS POR DEFECTO
-- =================================================================

INSERT INTO metodos_pago (nombre_metodo) VALUES 
('Efectivo'), 
('Transferencia'), 
('Tarjeta de Crédito/Débito');


INSERT INTO usuarios (nombre_usuario, password_hash, es_admin) VALUES 
('admin', 'temporal123', 1);