import pymysql
from config import Config

def get_db_connection():
    config = Config()
    return pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )
