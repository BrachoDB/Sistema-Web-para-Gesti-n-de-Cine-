import pymysql
from config import Config

def get_db_connection():
    try:
        config = Config()
        conn = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
            port=config.MYSQL_PORT,
            ssl={'ssl_mode': 'REQUIRED'},
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Configuración para Aiven
        with conn.cursor() as cursor:
            cursor.execute("SET SESSION sql_require_primary_key = OFF;")
        return conn
        
    except Exception as e:
        print(f"ERROR: No se pudo conectar a la base de datos. Verifica tus variables de entorno.")
        print(f"Detalle del error: {str(e)}")
        return None
