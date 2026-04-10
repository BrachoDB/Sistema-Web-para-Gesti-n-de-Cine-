import pymysql
import logging
from config import Config

logger = logging.getLogger(__name__)

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
        logger.error(f"Error crítico: No se pudo conectar a la base de datos.")
        logger.debug(f"Detalle técnico de la conexión fallida: {str(e)}")
        return None
