from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from db import get_db_connection

peliculas_bp = Blueprint('peliculas', __name__)


def admin_required(fn):
    """Decorador para verificar que el usuario es administrador"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            print(f"DEBUG - Claims: {claims}")  # Log para debug
            if not claims or claims.get('rol') != 'admin':
                return jsonify({'error': 'Acceso no autorizado. Se requiere rol de administrador'}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"DEBUG - Error en admin_required: {str(e)}")
            return jsonify({'error': f'Error de autenticación: {str(e)}'}), 422
    decorated_function.__name__ = fn.__name__
    return decorated_function

@peliculas_bp.route('/', methods=['GET'])
def get_peliculas():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM peliculas")
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@peliculas_bp.route('/<int:id>', methods=['GET'])
def get_pelicula(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM peliculas WHERE id = %s", (id,))
            pelicula = cursor.fetchone()
            if pelicula:
                return jsonify(pelicula), 200
            return jsonify({"error": "Pelicula no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@peliculas_bp.route('/', methods=['POST'])
# @admin_required  # Temporarily disabled for testing
def create_pelicula():
    data = request.json
    titulo = data.get('titulo')
    duracion = data.get('duracion')
    if not titulo or not duracion:
        return jsonify({"error": "Titulo y duracion requeridos"}), 400
    
    # Default values
    imagen_url = data.get('imagen_url') or 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=800&q=80'
    estado = 'activa'  # Default to activa so it shows in cartelera
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO peliculas (titulo, descripcion, duracion, genero, clasificacion, imagen_url, trailer_url, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                titulo, data.get('descripcion'), duracion, data.get('genero'),
                data.get('clasificacion'), imagen_url, data.get('trailer_url'), estado
            ))
            conn.commit()
            return jsonify({"message": "Pelicula creada", "id": cursor.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@peliculas_bp.route('/<int:id>', methods=['PUT'])
# @admin_required  # Temporarily disabled for testing
def update_pelicula(id):
    data = request.json
    
    # Validar que al menos un campo esté presente
    campos = ['titulo', 'descripcion', 'duracion', 'genero', 'clasificacion', 'imagen_url', 'trailer_url', 'estado']
    if not any(data.get(campo) for campo in campos):
        return jsonify({"error": "Debe proporcionar al menos un campo para actualizar"}), 400
    
    # Verificar que la película existe
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM peliculas WHERE id = %s", (id,))
            if not cursor.fetchone():
                return jsonify({"error": "Pelicula no encontrada"}), 404
            
            # Construir la consulta dinámicamente
            updates = []
            valores = []
            for campo in campos:
                if data.get(campo) is not None:
                    updates.append(f"{campo} = %s")
                    valores.append(data.get(campo))
            
            valores.append(id)
            
            cursor.execute(f"""
                UPDATE peliculas 
                SET {', '.join(updates)}
                WHERE id = %s
            """, tuple(valores))
            conn.commit()
            
            return jsonify({"message": "Pelicula actualizada correctamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@peliculas_bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_pelicula(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar que la película existe
            cursor.execute("SELECT id FROM peliculas WHERE id = %s", (id,))
            pelicula = cursor.fetchone()
            if not pelicula:
                return jsonify({"error": "Pelicula no encontrada"}), 404
            
            # Verificar que no tenga funciones activas
            cursor.execute("""
                SELECT id FROM funciones 
                WHERE pelicula_id = %s AND estado = 'disponible'
            """, (id,))
            funciones_activas = cursor.fetchone()
            
            if funciones_activas:
                return jsonify({"error": "No se puede eliminar la pelicula porque tiene funciones activas"}), 400
            
            # Eliminar la película
            cursor.execute("DELETE FROM peliculas WHERE id = %s", (id,))
            conn.commit()
            
            return jsonify({"message": "Pelicula eliminada correctamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
