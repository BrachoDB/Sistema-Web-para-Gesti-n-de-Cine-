from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Deshabilitar redirect automático de slashes
    app.url_map.strict_slashes = False
    # JWT_SECRET_KEY debe configurarse en variable de entorno (config.py)
    
    # Configuración CORS - permitir origen del frontend
    CORS(app, origins=["http://127.0.0.1:5500", "http://localhost:5500"], 
         allow_headers=["Content-Type", "Authorization", "Accept"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
    
    jwt = JWTManager(app)
    
    # Manejadores de errores JWT
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Token inválido', 'details': str(error)}), 422
    
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
        return jsonify({"status": "ok"}), 200
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
