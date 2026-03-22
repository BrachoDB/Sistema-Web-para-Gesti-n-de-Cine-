import pymysql
from config import Config

def get_db_connection():
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
    # Algunos proveedores como Aiven requieren esta configuración si el esquema no es perfecto
    with conn.cursor() as cursor:
        cursor.execute("SET SESSION sql_require_primary_key = OFF;")
    return conn
