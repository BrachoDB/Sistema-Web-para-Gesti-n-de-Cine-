"""
Script para inicializar la base de datos del sistema de cine.
Crea la base de datos, tablas, asientos y usuario admin.
"""
import pymysql
from pymysql.constants import CLIENT
import os
from config import Config


def crear_tablas(cursor):
    """Crea todas las tablas necesarias."""
    print("  - Tabla: usuarios")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            contrasena VARCHAR(255) NOT NULL,
            rol ENUM('admin', 'cliente') DEFAULT 'cliente',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("  - Tabla: peliculas")
    cursor.execute("""
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
        )
    """)
    
    print("  - Tabla: funciones")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pelicula_id INT NOT NULL,
            fecha DATE NOT NULL,
            hora TIME NOT NULL,
            sala VARCHAR(50) DEFAULT 'Sala 1',
            precio DECIMAL(10, 2) NOT NULL,
            estado ENUM('disponible', 'cancelada') DEFAULT 'disponible',
            FOREIGN KEY (pelicula_id) REFERENCES peliculas(id) ON DELETE CASCADE
        )
    """)
    
    print("  - Tabla: asientos")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asientos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            numero INT NOT NULL,
            fila VARCHAR(5) NOT NULL,
            columna INT NOT NULL,
            estado ENUM('activo', 'inactivo') DEFAULT 'activo'
        )
    """)
    
    print("  - Tabla: tiquetes")
    cursor.execute("""
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
        )
    """)
    
    print("  - Tabla: detalle_tiquete")
    cursor.execute("""
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
        )
    """)


def insertar_asientos(cursor):
    """Inserta los 150 asientos (10 filas A-J x 15 columnas)."""
    print("  Insertando asientos (10 filas x 15 columnas = 150 asientos)...")
    
    # Verificar si ya hay asientos
    cursor.execute("SELECT COUNT(*) FROM asientos")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  Ya existen {count} asientos en la base de datos.")
        return
    
    # Generar los 150 asientos
    asientos = []
    numero = 1
    for fila_num in range(1, 11):  # Filas 1-10 (A-J)
        fila = chr(64 + fila_num)  # A=65, B=66, etc.
        for columna in range(1, 16):  # Columnas 1-15
            asientos.append((numero, fila, columna))
            numero += 1
    
    # Insertar en lotes
    cursor.executemany(
        "INSERT IGNORE INTO asientos (numero, fila, columna) VALUES (%s, %s, %s)",
        asientos
    )
    print(f"  ✓ {len(asientos)} asientos insertados correctamente.")


def insertar_admin(cursor):
    """Inserta el usuario admin por defecto."""
    print("  Insertando usuario admin...")
    
    # Verificar si ya existe el admin
    cursor.execute("SELECT id FROM usuarios WHERE email = 'admin@cine.com'")
    if cursor.fetchone():
        print("  El usuario admin@cine.com ya existe.")
        return
    
    # Usar contraseña fija para desarrollo
    admin_password = 'admin123'
    
    # Hash de la contraseña
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(admin_password)
    
    cursor.execute(
        "INSERT INTO usuarios (nombre, email, contrasena, rol) VALUES (%s, %s, %s, %s)",
        ('Admin Cine', 'admin@cine.com', hashed_password, 'admin')
    )
    print(f"  ✓ Usuario admin creado: admin@cine.com")
    print(f"  ⚠ CONTRASEÑA: {admin_password}")
    print(f"  ⚠ CAMBIE ESTA CONTRASEÑA TRAS EL PRIMER INICIO DE SESIÓN")


def init_db():
    """Función principal para inicializar la base de datos."""
    print("\n" + "="*50)
    print("  INICIALIZANDO BASE DE DATOS - CINE BRACHO")
    print("="*50 + "\n")
    
    try:
        config = Config()
        
        # Conectar a MySQL sin seleccionar base de datos
        print(f"1. Conectando a MySQL en {config.MYSQL_HOST}...")
        conn = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            client_flag=CLIENT.MULTI_STATEMENTS
        )
        print("   ✓ Conexión establecida.\n")
        
        # Crear base de datos si no existe
        print(f"2. Creando base de datos '{config.MYSQL_DB}'...")
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DB}")
        print("   ✓ Base de datos creada/verificada.\n")
        
        # Seleccionar la base de datos
        conn.select_db(config.MYSQL_DB)
        
        # Crear tablas
        print("3. Creando tablas...")
        with conn.cursor() as cursor:
            crear_tablas(cursor)
        print("   ✓ Todas las tablas creadas.\n")
        
        # Insertar asientos
        print("4. Insertando asientos...")
        with conn.cursor() as cursor:
            insertar_asientos(cursor)
        print()
        
        # Insertar admin
        print("5. Creando usuario administrador...")
        with conn.cursor() as cursor:
            insertar_admin(cursor)
        print()
        
        # Confirmar cambios
        conn.commit()
        
        print("="*50)
        print("  ✅ Base de datos inicializada correctamente")
        print("="*50)
        print(f"\n  Usuario admin: admin@cine.com")
        print(f"  ⚠ La contraseña temporal fue mostrada arriba")
        print(f"  ⚠ CAMBIE LA CONTRASEÑA TRAS INICIAR SESIÓN")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == '__main__':
    init_db()
