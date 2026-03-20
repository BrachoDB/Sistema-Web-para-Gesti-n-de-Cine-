from flask import Blueprint, jsonify, request
from db import get_db_connection

funciones_bp = Blueprint('funciones', __name__)

@funciones_bp.route('/', methods=['GET'])
def get_funciones():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Join with peliculas to get the movie title
            sql = """
                SELECT f.*, p.titulo, p.imagen_url 
                FROM funciones f 
                JOIN peliculas p ON f.pelicula_id = p.id
                WHERE f.estado = 'disponible'
            """
            cursor.execute(sql)
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@funciones_bp.route('/<int:id>/asientos', methods=['GET'])
def get_asientos_funcion(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Setup querying all seats and join to find which are occupied for this specific function
            sql = """
                SELECT a.*, 
                CASE WHEN dt.id IS NOT NULL THEN 'ocupado' ELSE 'disponible' END as estado_funcion
                FROM asientos a
                LEFT JOIN detalle_tiquete dt ON a.id = dt.asiento_id AND dt.funcion_id = %s
            """
            cursor.execute(sql, (id,))
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@funciones_bp.route('/', methods=['POST'])
def create_funcion():
    data = request.json
    pelicula_id = data.get('pelicula_id')
    fecha = data.get('fecha')
    hora = data.get('hora')
    precio = data.get('precio')
    
    if not all([pelicula_id, fecha, hora, precio]):
        return jsonify({"error": "Faltan datos requeridos"}), 400
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO funciones (pelicula_id, fecha, hora, sala, precio)
                VALUES (%s, %s, %s, %s, %s)
            """, (pelicula_id, fecha, hora, data.get('sala', 'Sala 1'), precio))
            conn.commit()
            return jsonify({"message": "Funcion creada", "id": cursor.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
