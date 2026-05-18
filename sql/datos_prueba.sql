USE elotito_regio_db;

-- ────────────── ୨୧ ────────────────
-- ════ 1. CATÁLOGOS BASE ════
-- ────────────── ୨୧ ────────────────

INSERT INTO roles (nombre_rol, es_admin) VALUES 
('Administrador', 1),
('Staff Ventas', 0);

INSERT INTO metodos_pago (nombre_metodo) VALUES 
('Efectivo'),
('Transferencia SPEI'),
('Tarjeta (Terminal)');

INSERT INTO unidades_medida (nombre_unidad) VALUES 
('Pieza(s)'),
('Kilogramo(s)'),
('Litro(s)'),
('Paquete/Caja');

-- ────────────── ୨୧ ────────────────
-- ════ 2. USUARIOS (STAFF) ════
-- ────────────── ୨୧ ────────────────
-- NOTA: El password_hash es un cifrado irrompible. Si tienes problemas 
-- iniciando sesión con estos, crea uno nuevo desde la app temporalmente.

INSERT INTO usuarios (id_rol, nombre_usuario, nombre, apellido_paterno, apellido_materno, telefono, password_hash) VALUES 
(1, 'admin', 'Ana', 'Rosales', 'García', '8123456780', 'scrypt:32768:8:1$iGtJcFBc2XQWosNE$a2d3cd7b873ca62a061c0182c1c7879eda2989f7fc4cf89de59f6137fbd57d71c9f93a4d37a8161fdb065ad4ccc7ed7653a3637da5af281481ada92bf6264783'), 
(2, 'ventas1', 'Carlos', 'Martínez', NULL, '8123456781', 'scrypt:32768:8:1$iGtJcFBc2XQWosNE$a2d3cd7b873ca62a061c0182c1c7879eda2989f7fc4cf89de59f6137fbd57d71c9f93a4d37a8161fdb065ad4ccc7ed7653a3637da5af281481ada92bf6264783');

-- ────────────── ୨୧ ────────────────
-- ════ 3. CLIENTES ════
-- ────────────── ୨୧ ────────────────

INSERT INTO clientes (nombre, apellido_paterno, apellido_materno, telefono, email) VALUES 
('María', 'González', 'López', '8111222333', 'maria.glz@email.com'),
('Roberto', 'Sánchez', NULL, '8188990011', 'roberto.s@email.com'),
('Laura', 'Gómez', 'Treviño', '8144556677', NULL);

-- ────────────── ୨୧ ────────────────
-- ════ 4. PROVEEDORES ════
-- ────────────── ୨୧ ────────────────

INSERT INTO proveedores (nombre_empresa, contacto_nombre, contacto_apellido_paterno, contacto_apellido_materno, razon_social, rfc, telefono, email) VALUES 
('Maíz Central MTY', 'Javier', 'Hernández', 'Cantú', 'Maíz y Granos del Norte SA de CV', 'MGN901010ABC', '8100112233', 'ventas@maizcentral.com'),
('Desechables Regios', 'Patricia', 'Cantú', NULL, 'Plásticos y Desechables Regios SRL', 'PDR800505XYZ', '8155443322', 'contacto@desechablesmty.com');

-- ────────────── ୨୧ ────────────────
-- ════ 5. PAQUETES (PRODUCTOS) ════
-- ────────────── ୨୧ ────────────────

INSERT INTO paquetes (nombre_paquete, descripcion, precio, costo) VALUES 
('Carrito Clásico (50 pzas)', 'Incluye 50 elotes en vaso, aderezos tradicionales y servicio por 2 horas.', 2500.00, 750.00),
('Carrito VIP (100 pzas)', 'Incluye 100 elotes, aderezos premium (conchitas, cacahuates) y servicio por 3 horas.', 4500.00, 1800.00);

-- ────────────── ୨୧ ────────────────
-- ════ 6. INSUMOS ════
-- ────────────── ୨୧ ────────────────

INSERT INTO insumos (nombre_insumo, costo_unitario, id_unidad, id_proveedor) VALUES 
('Elote en grano desgranado', 35.50, 2, 1),      -- 2: Kg (Maíz Central)
('Mayonesa Clásica', 85.00, 2, NULL),            -- 2: Kg
('Queso rallado', 120.00, 2, NULL),              -- 2: Kg
('Mantequilla', 90.00, 2, NULL),                 -- 2: Kg
('Vasos térmicos 8oz', 45.00, 4, 2),             -- 4: Paquete (Desechables)
('Cucharas de plástico', 25.00, 4, 2);           -- 4: Paquete (Desechables)

-- ────────────── ୨୧ ────────────────
-- ════ 7. RECETA DE PAQUETES (PIVOTE) ════
-- ────────────── ୨୧ ────────────────
-- Armamos el Paquete 1 (Clásico 50 pzas)

INSERT INTO paquete_insumo (id_paquete, id_insumo, cantidad_necesaria) VALUES 
(1, 1, 5.00),  -- 5 kg de elote
(1, 2, 1.50),  -- 1.5 kg mayonesa
(1, 3, 1.00),  -- 1 kg queso
(1, 4, 0.50),  -- 0.5 kg mantequilla
(1, 5, 1.00),  -- 1 paquete de vasos
(1, 6, 1.00);  -- 1 paquete de cucharas

-- ────────────── ୨୧ ────────────────
-- ════ 8. EVENTOS (AGENDA) ════
-- ────────────── ୨୧ ────────────────

INSERT INTO eventos (id_cliente, id_usuario, fecha_evento, hora_evento, lugar, adelanto, id_metodo_pago) VALUES 
(1, 1, '2024-12-15', '16:00:00', 'Salón de Fiestas "El Edén", Apodaca', 500.00, 2), -- Transf SPEI
(2, 2, '2024-12-20', '19:30:00', 'Quinta "Los Pinos", Carretera Nacional', 1000.00, 1); -- Efectivo

-- ────────────── ୨୧ ────────────────
-- ════ 9. VENTAS DEL EVENTO (PIVOTE) ════
-- ────────────── ୨୧ ────────────────

INSERT INTO evento_paquete (id_evento, id_paquete, cantidad) VALUES 
(1, 1, 1), -- El evento 1 contrató 1 carrito clásico
(2, 2, 1); -- El evento 2 contrató 1 carrito VIP