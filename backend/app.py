from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    
    # Import routes
    from routes.peliculas import peliculas_bp
    from routes.funciones import funciones_bp
    from routes.tiquetes import tiquetes_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(peliculas_bp, url_prefix='/api/peliculas')
    app.register_blueprint(funciones_bp, url_prefix='/api/funciones')
    app.register_blueprint(tiquetes_bp, url_prefix='/api/tiquetes')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    @app.route('/health')
    def health_check():
        return jsonify({"status": "ok"}), 200
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
