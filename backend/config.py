import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'cine_db')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-cinema-123')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-cinema-456')
    
    # Validar que las claves de seguridad estén configuradas (Warning en log si faltan)
    if os.getenv('SECRET_KEY') is None:
        print("WARNING: SECRET_KEY no está configurada, usando valor por defecto")
    if os.getenv('JWT_SECRET_KEY') is None:
        print("WARNING: JWT_SECRET_KEY no está configurada, usando valor por defecto")
