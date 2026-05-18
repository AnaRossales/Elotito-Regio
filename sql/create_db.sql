CREATE DATABASE elotito_regio_db;
USE elotito_regio_db;

CREATE TABLE roles (
    id_rol TINYINT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(30) NOT NULL UNIQUE,
    es_admin TINYINT(1) NOT NULL DEFAULT 0
);

CREATE TABLE metodos_pago (
    id_metodo TINYINT AUTO_INCREMENT PRIMARY KEY,
    nombre_metodo VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE unidades_medida (
    id_unidad TINYINT AUTO_INCREMENT PRIMARY KEY,
    nombre_unidad VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_rol TINYINT NOT NULL,
    nombre_usuario VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(30) NOT NULL,
    apellido_materno VARCHAR(30) DEFAULT NULL,
    telefono CHAR(15) DEFAULT NULL,
    password_hash VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(30) NOT NULL,
    apellido_materno VARCHAR(30) DEFAULT NULL,
    telefono CHAR(15) DEFAULT NULL,
    email VARCHAR(80) DEFAULT NULL
);

CREATE TABLE proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(80) NOT NULL,
    contacto_nombre VARCHAR(50) DEFAULT NULL,
    contacto_apellido_paterno VARCHAR(30) DEFAULT NULL,
    contacto_apellido_materno VARCHAR(30) DEFAULT NULL,
    razon_social VARCHAR(100) DEFAULT NULL,
    rfc VARCHAR(13) DEFAULT NULL,
    telefono CHAR(20) DEFAULT NULL,
    email VARCHAR(80) DEFAULT NULL
);

CREATE TABLE paquetes (
    id_paquete SMALLINT AUTO_INCREMENT PRIMARY KEY,
    nombre_paquete VARCHAR(60) NOT NULL,
    descripcion TEXT DEFAULT NULL,
    precio DECIMAL(10,2) NOT NULL,
    costo DECIMAL(10,2) NOT NULL
);

CREATE TABLE insumos (
    id_insumo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_insumo VARCHAR(60) NOT NULL,
    costo_unitario DECIMAL(10,2) NOT NULL,
    id_unidad TINYINT NOT NULL,
    id_proveedor INT DEFAULT NULL,
    FOREIGN KEY (id_unidad) REFERENCES unidades_medida(id_unidad),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE eventos (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha_evento DATE NOT NULL,
    hora_evento TIME NOT NULL,
    lugar VARCHAR(150) NOT NULL,
    adelanto DECIMAL(10,2) DEFAULT 0.00,
    id_metodo_pago TINYINT DEFAULT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_metodo_pago) REFERENCES metodos_pago(id_metodo)
);

CREATE TABLE paquete_insumo (
    id_paquete SMALLINT NOT NULL,
    id_insumo INT NOT NULL,
    cantidad_necesaria DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_paquete, id_insumo),
    FOREIGN KEY (id_paquete) REFERENCES paquetes(id_paquete) ON DELETE CASCADE,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo) ON DELETE CASCADE
);

CREATE TABLE evento_paquete (
    id_evento INT NOT NULL,
    id_paquete SMALLINT NOT NULL,
    cantidad SMALLINT NOT NULL DEFAULT 1,
    PRIMARY KEY (id_evento, id_paquete),
    FOREIGN KEY (id_evento) REFERENCES eventos(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_paquete) REFERENCES paquetes(id_paquete)
);