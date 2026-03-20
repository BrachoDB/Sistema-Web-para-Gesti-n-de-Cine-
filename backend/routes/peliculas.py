from flask import Blueprint, jsonify, request
from db import get_db_connection

peliculas_bp = Blueprint('peliculas', __name__)

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
def create_pelicula():
    data = request.json
    titulo = data.get('titulo')
    duracion = data.get('duracion')
    if not titulo or not duracion:
        return jsonify({"error": "Titulo y duracion requeridos"}), 400
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO peliculas (titulo, descripcion, duracion, genero, clasificacion, imagen_url, trailer_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                titulo, data.get('descripcion'), duracion, data.get('genero'),
                data.get('clasificacion'), data.get('imagen_url'), data.get('trailer_url')
            ))
            conn.commit()
            return jsonify({"message": "Pelicula creada", "id": cursor.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
