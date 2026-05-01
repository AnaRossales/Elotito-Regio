USE `elotito_regio_db`;

-- --------------------------------------------------------
-- 1. USUARIOS (1 Admin y 1 Staff para pruebas)
-- La contraseña de ambos es: 12345 (basado en tu hash original)
-- --------------------------------------------------------
INSERT INTO `usuarios` (`id_usuario`, `nombre_usuario`, `password_hash`, `es_admin`) VALUES
(1, 'admin', 'scrypt:32768:8:1$UUDpxI5SRjyMqbxv$8b90b9609668f29ddf12495d99fc00afaea44e97d7513f6c6b8bd310efdaf8c541af53742061217003debb0b56bc9bea1533ccecb7375a09ec522c308bd8476f', 1),
(2, 'staff', 'scrypt:32768:8:1$UUDpxI5SRjyMqbxv$8b90b9609668f29ddf12495d99fc00afaea44e97d7513f6c6b8bd310efdaf8c541af53742061217003debb0b56bc9bea1533ccecb7375a09ec522c308bd8476f', 0);

-- --------------------------------------------------------
-- 2. MÉTODOS DE PAGO
-- --------------------------------------------------------
INSERT INTO `metodos_pago` (`id_metodo`, `nombre_metodo`) VALUES
(1, 'Efectivo'),
(2, 'Transferencia'),
(3, 'Tarjeta de Crédito/Débito');

-- --------------------------------------------------------
-- 3. PROVEEDORES
-- --------------------------------------------------------
INSERT INTO `proveedores` (`id_proveedor`, `nombre_empresa`, `contacto_nombre`, `razon_social`, `rfc`, `telefono`, `email`) VALUES
(1, 'Agropecuaria El Maizal', 'Carlos Garza', 'El Maizal SA de CV', 'MAIZ123456789', '8112345678', 'ventas@elmaizal.com'),
(2, 'Lácteos del Norte', 'Ana Sofía', 'Lácteos MTY S de RL', 'LACN987654321', '8187654321', 'pedidos@lacteosnorte.com'),
(3, 'Desechables Regios', 'Roberto Martínez', 'Plásticos y Más SA', 'PLAS112233445', '8100112233', 'contacto@desechables.com');

-- --------------------------------------------------------
-- 4. CLIENTES
-- --------------------------------------------------------
INSERT INTO `clientes` (`id_cliente`, `nombre`, `apellido_paterno`, `apellido_materno`, `telefono`, `email`) VALUES
(1, 'María', 'González', 'López', '8123456789', 'maria.glz@email.com'),
(2, 'Roberto', 'Sánchez', 'Pérez', '8198765432', 'roberto.sp@email.com'),
(3, 'Familia', 'Treviño', 'Cantú', '8155554444', 'eventos.trevino@email.com');

-- --------------------------------------------------------
-- 5. PAQUETES (Catálogo de ventas)
-- --------------------------------------------------------
INSERT INTO `paquetes` (`id_paquete`, `nombre_paquete`, `descripcion`, `precio`) VALUES
(1, 'Paquete Básico 50', 'Servicio para 50 personas. Incluye elote en vaso, aderezos y desechables.', 2500.00),
(2, 'Paquete Fiesta 100', 'Servicio para 100 personas. Incluye personal de servicio y barra de toppings.', 4500.00),
(3, 'Paquete Premium Elote Entero', '50 Elotes enteros asados con ingredientes de primera calidad.', 3200.00);

-- --------------------------------------------------------
-- 6. INSUMOS (Asociados a los proveedores que creamos)
-- --------------------------------------------------------
INSERT INTO `insumos` (`id_insumo`, `nombre_insumo`, `costo_unitario`, `unidad_medida`, `id_proveedor`) VALUES
(1, 'Grano de Elote Blanco', 45.00, 'kg', 1),
(2, 'Grano de Elote Amarillo', 48.00, 'kg', 1),
(3, 'Mayonesa (frasco 3.5kg)', 280.00, 'pza', NULL),
(4, 'Queso Parmesano', 120.00, 'kg', 2),
(5, 'Mantequilla', 95.00, 'kg', 2),
(6, 'Chile en polvo', 85.00, 'kg', NULL),
(7, 'Limón', 25.00, 'kg', NULL),
(8, 'Vaso Térmico 8oz', 1.20, 'pza', 3),
(9, 'Cuchara de plástico', 0.40, 'pza', 3),
(10, 'Servilletas (pqte 500)', 45.00, 'pza', 3);

-- --------------------------------------------------------
-- 7. PAQUETE_INSUMO (Las "Recetas" de cada paquete)
-- --------------------------------------------------------
INSERT INTO `paquete_insumo` (`id_paquete`, `id_insumo`, `cantidad_necesaria`) VALUES
(1, 1, 10.00), -- 10kg de elote para 50 personas
(1, 3, 0.50),  -- Media mayonesa
(1, 4, 1.50),  -- 1.5kg de queso
(1, 8, 50.00), -- 50 vasos
(1, 9, 50.00), -- 50 cucharas
(2, 1, 20.00), -- 20kg para 100 personas
(2, 3, 1.00),  -- 1 mayonesa entera
(2, 8, 100.00),-- 100 vasos
(3, 2, 15.00); -- Elote amarillo para el premium

-- --------------------------------------------------------
-- 8. EVENTOS (La agenda / ventas realizadas)
-- --------------------------------------------------------
INSERT INTO `eventos` (`id_evento`, `id_cliente`, `id_usuario`, `fecha_evento`, `hora_evento`, `lugar`, `adelanto`, `id_metodo_pago`) VALUES
(1, 1, 1, '2026-05-15', '14:00:00', 'Quinta Los Rosales, Carretera Nacional', 1000.00, 2), -- Pago por transferencia, debe 1500
(2, 2, 2, '2026-05-20', '19:30:00', 'Salón Fiesta Real, San Nicolás', 4500.00, 1), -- Liquidado en efectivo
(3, 3, 1, '2026-06-05', '16:00:00', 'Domicilio Particular (Mitras Centro)', 500.00, 3); -- Pago con tarjeta, anticipo pequeño

-- --------------------------------------------------------
-- 9. EVENTO_PAQUETE (Qué compró cada cliente en su evento)
-- --------------------------------------------------------
INSERT INTO `evento_paquete` (`id_evento`, `id_paquete`, `cantidad`) VALUES
(1, 1, 1), -- El evento 1 compró un Paquete Básico 50 (Total: 2500)
(2, 2, 1), -- El evento 2 compró un Paquete Fiesta 100 (Total: 4500)
(3, 3, 1), -- El evento 3 compró un Paquete Premium (Total: 3200)
(3, 1, 1); -- Y también un Básico 50 (Total del evento 3: 5700)