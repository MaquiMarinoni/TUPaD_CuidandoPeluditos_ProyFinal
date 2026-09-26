-- =============================================================================
-- TRABAJO INTEGRADOR FINAL | CUIDANDO PELUDITOS (TUPaD - UTN)
-- Script DML: Datos Semilla e Iniciales
-- =============================================================================

-- 1. Roles del Sistema
INSERT INTO roles (id, nombre) VALUES 
(1, 'DUENO'),
(2, 'CUIDADOR'),
(3, 'ADMIN')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);