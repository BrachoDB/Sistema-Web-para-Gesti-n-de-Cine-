CREATE DATABASE IF NOT EXISTS cine_db;
USE cine_db;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'cliente') DEFAULT 'cliente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS peliculas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    duracion INT NOT NULL COMMENT 'Duración en minutos',
    genero VARCHAR(50),
    clasificacion VARCHAR(20),
    imagen_url VARCHAR(255),
    trailer_url VARCHAR(255),
    estado ENUM('activa', 'inactiva') DEFAULT 'activa'
);

CREATE TABLE IF NOT EXISTS funciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pelicula_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    sala VARCHAR(50) DEFAULT 'Sala 1',
    precio DECIMAL(10, 2) NOT NULL,
    estado ENUM('disponible', 'cancelada') DEFAULT 'disponible',
    FOREIGN KEY (pelicula_id) REFERENCES peliculas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS asientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero INT NOT NULL,
    fila VARCHAR(5) NOT NULL,
    columna INT NOT NULL,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
);

CREATE TABLE IF NOT EXISTS tiquetes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    usuario_id INT NULL,
    funcion_id INT NOT NULL,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) NOT NULL,
    estado ENUM('valido', 'usado', 'invalido') DEFAULT 'valido',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (funcion_id) REFERENCES funciones(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS detalle_tiquete (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tiquete_id INT NOT NULL,
    funcion_id INT NOT NULL,
    asiento_id INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (tiquete_id) REFERENCES tiquetes(id) ON DELETE CASCADE,
    FOREIGN KEY (funcion_id) REFERENCES funciones(id) ON DELETE CASCADE,
    FOREIGN KEY (asiento_id) REFERENCES asientos(id) ON DELETE CASCADE,
    UNIQUE (funcion_id, asiento_id)
);

DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS InsertarAsientos()
BEGIN
    DECLARE v_fila CHAR(1);
    DECLARE v_columna INT;
    DECLARE v_numero INT;
    DECLARE v_fila_num INT;
    DECLARE v_count INT;
    
    SELECT COUNT(*) INTO v_count FROM asientos;
    
    IF v_count = 0 THEN
        SET v_numero = 1;
        SET v_fila_num = 1;
        
        WHILE v_fila_num <= 10 DO
            SET v_columna = 1;
            SET v_fila = CHAR(64 + v_fila_num); -- A = 65
            WHILE v_columna <= 15 DO
                INSERT IGNORE INTO asientos (numero, fila, columna) VALUES (v_numero, v_fila, v_columna);
                SET v_numero = v_numero + 1;
                SET v_columna = v_columna + 1;
            END WHILE;
            SET v_fila_num = v_fila_num + 1;
        END WHILE;
    END IF;
END$$
DELIMITER ;

CALL InsertarAsientos();

-- Insert a default admin user for initial testing
INSERT IGNORE INTO usuarios (nombre, email, contrasena, rol) VALUES ('Admin Cine', 'admin@cine.com', 'admin123', 'admin');
