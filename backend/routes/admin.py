from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
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
            
            # Convertir objetos time a strings para JSON
            ocupacion_serializada = []
            for row in ocupacion:
                row_dict = dict(row)
                if row_dict.get('hora'):
                    row_dict['hora'] = str(row_dict['hora'])
                if row_dict.get('fecha'):
                    row_dict['fecha'] = str(row_dict['fecha'])
                ocupacion_serializada.append(row_dict)
            
            return jsonify({
                "total_ventas": float(total_ventas),
                "ocupacion": ocupacion_serializada
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@admin_bp.route('/ventas-por-dia', methods=['GET'])
def get_ventas_por_dia():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Reporte de ventas agrupadas por fecha
            sql = """
                SELECT 
                    DATE(fecha_compra) as fecha,
                    COUNT(*) as cantidad_tiquetes,
                    SUM(total) as total_ventas
                FROM tiquetes
                WHERE estado != 'invalido'
                GROUP BY DATE(fecha_compra)
                ORDER BY fecha DESC
            """
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            # Convertir fechas a string para JSON
            ventas_por_dia = []
            for row in resultados:
                ventas_por_dia.append({
                    "fecha": row["fecha"].strftime("%Y-%m-%d") if row["fecha"] else None,
                    "cantidad_tiquetes": row["cantidad_tiquetes"],
                    "total_ventas": float(row["total_ventas"]) if row["total_ventas"] else 0.0
                })
            
            return jsonify(ventas_por_dia), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@admin_bp.route('/peliculas-mas-vistas', methods=['GET'])
def get_peliculas_mas_vistas():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Top películas con más tiquetes vendidos
            sql = """
                SELECT 
                    p.id,
                    p.titulo,
                    p.genero,
                    COUNT(dt.id) as cantidad_tiquetes,
                    SUM(t.total) as total_recaudado
                FROM peliculas p
                JOIN funciones f ON p.id = f.pelicula_id
                JOIN detalle_tiquete dt ON f.id = dt.funcion_id
                JOIN tiquetes t ON dt.tiquete_id = t.id
                WHERE t.estado != 'invalido'
                GROUP BY p.id, p.titulo, p.genero
                ORDER BY cantidad_tiquetes DESC
                LIMIT 10
            """
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            # Formatear resultados
            peliculas = []
            for row in resultados:
                peliculas.append({
                    "id": row["id"],
                    "titulo": row["titulo"],
                    "genero": row["genero"],
                    "cantidad_tiquetes": row["cantidad_tiquetes"],
                    "total_recaudado": float(row["total_recaudado"]) if row["total_recaudado"] else 0.0
                })
            
            return jsonify(peliculas), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
