from flask import Blueprint, jsonify, request
from db import get_db_connection
import uuid

tiquetes_bp = Blueprint('tiquetes', __name__)

@tiquetes_bp.route('/', methods=['POST'])
def create_tiquete():
    data = request.json
    funcion_id = data.get('funcion_id')
    asientos = data.get('asientos', []) # array of asiento_id
    usuario_id = data.get('usuario_id', None)
    
    if not funcion_id or not asientos:
        return jsonify({"error": "funcion_id y asientos son requeridos"}), 400
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Revisa que la funcion exista
            cursor.execute("SELECT precio FROM funciones WHERE id = %s AND estado = 'disponible'", (funcion_id,))
            funcion = cursor.fetchone()
            if not funcion:
                return jsonify({"error": "Funcion no encontrada o no disponible"}), 404
                
            precio_unitario = funcion['precio']
            total = len(asientos) * precio_unitario
            
            # Start transaction explicitly
            conn.begin()
            
            # Check availability
            format_strings = ','.join(['%s'] * len(asientos))
            query = f"""
                SELECT asiento_id FROM detalle_tiquete 
                WHERE funcion_id = %s AND asiento_id IN ({format_strings})
            """
            cursor.execute(query, [funcion_id] + asientos)
            ocupados = cursor.fetchall()
            
            if ocupados:
                conn.rollback()
                return jsonify({"error": "Uno o mas asientos ya estan ocupados"}), 400
                
            # Create tiquete
            codigo = str(uuid.uuid4())[:8].upper()
            cursor.execute("""
                INSERT INTO tiquetes (codigo, usuario_id, funcion_id, total) 
                VALUES (%s, %s, %s, %s)
            """, (codigo, usuario_id, funcion_id, total))
            
            tiquete_id = cursor.lastrowid
            
            # Insert details
            for asiento_id in asientos:
                cursor.execute("""
                    INSERT INTO detalle_tiquete (tiquete_id, funcion_id, asiento_id, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (tiquete_id, funcion_id, asiento_id, precio_unitario))
                
            conn.commit()
            return jsonify({
                "message": "Compra exitosa",
                "tiquete": {"id": tiquete_id, "codigo": codigo, "total": total}
            }), 201
            
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@tiquetes_bp.route('/validar', methods=['POST'])
def validar_tiquete():
    data = request.json
    codigo = data.get('codigo')
    
    if not codigo:
        return jsonify({"error": "codigo requerido"}), 400
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, estado FROM tiquetes WHERE codigo = %s", (codigo,))
            tiquete = cursor.fetchone()
            
            if not tiquete:
                return jsonify({"estado": "Inválido"}), 200
                
            if tiquete['estado'] == 'usado':
                return jsonify({"estado": "Usado"}), 200
                
            if tiquete['estado'] == 'valido':
                cursor.execute("UPDATE tiquetes SET estado = 'usado' WHERE id = %s", (tiquete['id'],))
                conn.commit()
                return jsonify({"estado": "Válido"}), 200
                
            return jsonify({"estado": "Inválido"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
