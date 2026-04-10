import os
import sys
import logging

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Asegurar que el directorio 'backend' esté en el path para Vercel
sys.path.append(os.path.dirname(__file__))

from config import Config

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    app.url_map.strict_slashes = False
    
    CORS(app, origins=["*"], 
         allow_headers=["Content-Type", "Authorization", "Accept"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
    
    jwt = JWTManager(app)
    
    # Manejadores de errores JWT
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Token invalido', 'details': str(error)}), 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Token requerido', 'details': str(error)}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token expirado'}), 401
    
    # Import routes
    from routes.peliculas import peliculas_bp
    from routes.funciones import funciones_bp
    from routes.tiquetes import tiquetes_bp
    from routes.admin import admin_bp
    from routes.auth import auth_bp
    
    app.register_blueprint(peliculas_bp, url_prefix='/api/peliculas')
    app.register_blueprint(funciones_bp, url_prefix='/api/funciones')
    app.register_blueprint(tiquetes_bp, url_prefix='/api/tiquetes')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    @app.route('/health')
    def health_check():
        from db import get_db_connection
        db_status = "error"
        try:
            conn = get_db_connection()
            if conn:
                db_status = "connected"
                conn.close()
        except Exception as e:
            db_status = f"error: {str(e)}"
            
        return jsonify({
            "status": "ok",
            "database": db_status,
            "environment": os.getenv('VERCEL_ENV', 'development')
        }), 200
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
