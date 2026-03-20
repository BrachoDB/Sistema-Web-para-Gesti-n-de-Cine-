import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'cine_db')
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # Validar que las claves de seguridad estén configuradas
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY debe configurarse en variable de entorno")
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY debe configurarse en variable de entorno")
