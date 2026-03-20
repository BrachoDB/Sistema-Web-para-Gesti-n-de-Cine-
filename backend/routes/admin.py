from flask import Blueprint, jsonify, request
from db import get_db_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Total ventas
            cursor.execute("SELECT COALESCE(SUM(total), 0) as total_ventas FROM tiquetes WHERE estado != 'invalido'")
            total_ventas = cursor.fetchone()['total_ventas']
            
            # Ocupacion por funcion
            cursor.execute("""
                SELECT f.id, p.titulo, f.fecha, f.hora, 
                       COUNT(dt.id) as asientos_ocupados,
                       150 as capacidad_total
                FROM funciones f
                JOIN peliculas p ON f.pelicula_id = p.id
                LEFT JOIN detalle_tiquete dt ON f.id = dt.funcion_id
                GROUP BY f.id, p.titulo, f.fecha, f.hora
                ORDER BY f.fecha DESC, f.hora DESC
            """)
            ocupacion = cursor.fetchall()
            
            return jsonify({
                "total_ventas": float(total_ventas),
                "ocupacion": ocupacion
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
