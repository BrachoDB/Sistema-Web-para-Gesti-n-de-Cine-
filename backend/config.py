import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Prioridad 1: DATABASE_URL (URI completa)
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if DATABASE_URL:
        # Analizar la URI para extraer componentes
        _url = urlparse(DATABASE_URL)
        MYSQL_HOST = _url.hostname
        MYSQL_USER = _url.username
        MYSQL_PASSWORD = _url.password
        MYSQL_DB = _url.path[1:] if _url.path else os.getenv('DB_NAME')
        MYSQL_PORT = int(_url.port) if _url.port else 25560
    else:
        # Prioridad 2: Variables individuales (como están en tu Vercel)
        MYSQL_HOST = os.getenv('DB_HOST') or os.getenv('MYSQL_HOST')
        MYSQL_USER = os.getenv('DB_USER') or os.getenv('MYSQL_USER')
        MYSQL_PASSWORD = os.getenv('DB_PASSWORD') or os.getenv('MYSQL_PASSWORD')
        MYSQL_DB = os.getenv('DB_NAME') or os.getenv('MYSQL_DB')
        MYSQL_PORT = int(os.getenv('DB_PORT', 25560))

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-cinema-123')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-cinema-456')
    
    # Validar configuración crítica
    @classmethod
    def validate(cls):
        missing = []
        if not cls.MYSQL_HOST: missing.append("DB_HOST/DATABASE_URL")
        if not cls.MYSQL_USER: missing.append("DB_USER")
        if not cls.MYSQL_PASSWORD: missing.append("DB_PASSWORD")
        
        if missing:
            print(f"WARNING: Faltan variables de entorno críticas: {', '.join(missing)}")
            return False
        return True

# Validar al importar
Config.validate()
