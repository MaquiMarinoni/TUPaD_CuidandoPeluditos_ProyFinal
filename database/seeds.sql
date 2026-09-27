
-- 1. Roles del Sistema
INSERT INTO roles (id, nombre) VALUES 
(1, 'DUENO'),
(2, 'CUIDADOR'),
(3, 'ADMIN')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);