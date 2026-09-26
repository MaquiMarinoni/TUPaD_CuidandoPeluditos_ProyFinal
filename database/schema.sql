-- =============================================================================
-- TRABAJO INTEGRADOR FINAL | CUIDANDO PELUDITOS (TUPaD - UTN)
-- Script DDL: Creación de Esquema de Base de Datos Relacional
-- Motor: MySQL 8.x / MariaDB 10.x (InnoDB)
-- =============================================================================

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS incidencias;
DROP TABLE IF EXISTS valoraciones;
DROP TABLE IF EXISTS solicitudes_mascotas;
DROP TABLE IF EXISTS solicitudes;
DROP TABLE IF EXISTS disponibilidades;
DROP TABLE IF EXISTS mascotas;
DROP TABLE IF EXISTS perfiles_cuidadores;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS roles;
SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------
-- 1. Tabla: roles
-- -----------------------------------------------------
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 2. Tabla: usuarios
-- -----------------------------------------------------
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rol_id INT NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    telefono VARCHAR(30) NOT NULL,
    provincia VARCHAR(60) NOT NULL,
    localidad VARCHAR(60) NOT NULL,
    direccion VARCHAR(120) NOT NULL, -- Dato privado (Principio de minimización Ley 25.326)
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_roles FOREIGN KEY (rol_id) REFERENCES roles (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_ubicacion ON usuarios(provincia, localidad);

-- -----------------------------------------------------
-- 3. Tabla: perfiles_cuidadores
-- -----------------------------------------------------
CREATE TABLE perfiles_cuidadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL UNIQUE,
    descripcion TEXT NULL,
    capacidad_maxima INT NOT NULL DEFAULT 1, -- Cupo simultáneo máximo de mascotas
    admite_perros BOOLEAN NOT NULL DEFAULT TRUE,
    admite_gatos BOOLEAN NOT NULL DEFAULT TRUE,
    condiciones_convivencia TEXT NULL,
    tarifa_diaria DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_cuidadores_usuarios FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 4. Tabla: mascotas
-- -----------------------------------------------------
CREATE TABLE mascotas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dueno_id INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    especie VARCHAR(20) NOT NULL, -- 'PERRO' o 'GATO'
    raza VARCHAR(50) NULL,
    tamano VARCHAR(20) NOT NULL DEFAULT 'MEDIANO', -- 'CHICO', 'MEDIANO', 'GRANDE'
    fecha_nacimiento DATE NULL,
    cuidados_especiales TEXT NULL,
    contacto_veterinario VARCHAR(100) NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_mascotas_dueno FOREIGN KEY (dueno_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_mascotas_dueno ON mascotas(dueno_id);

-- -----------------------------------------------------
-- 5. Tabla: disponibilidades
-- -----------------------------------------------------
CREATE TABLE disponibilidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuidador_id INT NOT NULL,
    fecha_desde DATE NOT NULL,
    fecha_hasta DATE NOT NULL,
    modalidad VARCHAR(20) NOT NULL DEFAULT 'ALOJAMIENTO', -- 'ALOJAMIENTO' o 'VISITA'
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_disponibilidades_cuidador FOREIGN KEY (cuidador_id) REFERENCES perfiles_cuidadores (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_disponibilidades_fechas ON disponibilidades(cuidador_id, fecha_desde, fecha_hasta);

-- -----------------------------------------------------
-- 6. Tabla: solicitudes (Corazón del sistema de reservas)
-- -----------------------------------------------------
CREATE TABLE solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dueno_id INT NOT NULL,
    cuidador_id INT NOT NULL,
    modalidad VARCHAR(20) NOT NULL DEFAULT 'ALOJAMIENTO',
    fecha_desde DATE NOT NULL,
    fecha_hasta DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE', -- 'PENDIENTE', 'ACEPTADA', 'RECHAZADA', 'CANCELADA', 'EN_CURSO', 'FINALIZADA'
    total_mascotas INT NOT NULL DEFAULT 1,
    monto_total DECIMAL(10, 2) NULL,
    contacto_emergencia VARCHAR(100) NOT NULL,
    veterinario_emergencia VARCHAR(100) NULL,
    autorizacion_urgencia BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_solicitudes_dueno FOREIGN KEY (dueno_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_solicitudes_cuidador FOREIGN KEY (cuidador_id) REFERENCES perfiles_cuidadores (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_solicitudes_fechas_estado ON solicitudes(cuidador_id, fecha_desde, fecha_hasta, estado);
CREATE INDEX idx_solicitudes_dueno ON solicitudes(dueno_id);

-- -----------------------------------------------------
-- 7. Tabla: solicitudes_mascotas (Snapshot histórico)
-- -----------------------------------------------------
CREATE TABLE solicitudes_mascotas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solicitud_id INT NOT NULL,
    mascota_id INT NOT NULL,
    nombre_snapshot VARCHAR(50) NOT NULL,
    especie_snapshot VARCHAR(20) NOT NULL,
    cuidados_snapshot TEXT NULL,
    CONSTRAINT fk_sol_masc_solicitud FOREIGN KEY (solicitud_id) REFERENCES solicitudes (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sol_masc_mascota FOREIGN KEY (mascota_id) REFERENCES mascotas (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 8. Tabla: valoraciones (Reseña única verificada post-servicio)
-- -----------------------------------------------------
CREATE TABLE valoraciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solicitud_id INT NOT NULL UNIQUE, -- Restricción de unicidad: 1 sola valoración por servicio
    dueno_id INT NOT NULL,
    cuidador_id INT NOT NULL,
    puntaje TINYINT NOT NULL,
    comentario TEXT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_valoracion_puntaje CHECK (puntaje BETWEEN 1 AND 5),
    CONSTRAINT fk_valoraciones_solicitud FOREIGN KEY (solicitud_id) REFERENCES solicitudes (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_valoraciones_dueno FOREIGN KEY (dueno_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_valoraciones_cuidador FOREIGN KEY (cuidador_id) REFERENCES perfiles_cuidadores (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 9. Tabla: incidencias (Protocolo de imprevistos)
-- -----------------------------------------------------
CREATE TABLE incidencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solicitud_id INT NOT NULL,
    reportado_por_id INT NOT NULL,
    tipo VARCHAR(30) NOT NULL, -- 'SALUD', 'CONDUCTA', 'EXTRAVIO', 'OTRO'
    descripcion TEXT NOT NULL,
    medidas_tomadas TEXT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'ABIERTA', -- 'ABIERTA', 'RESUELTA'
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_incidencias_solicitud FOREIGN KEY (solicitud_id) REFERENCES solicitudes (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_incidencias_usuario FOREIGN KEY (reportado_por_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;