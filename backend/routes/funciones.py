from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection

funciones_bp = Blueprint('funciones', __name__)


def admin_required(fn):
    """Decorador para verificar que el usuario es administrador"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        identity = get_jwt_identity()
        if identity.get('rol') != 'admin':
            return jsonify({'error': 'Acceso no autorizado. Se requiere rol de administrador'}), 403
        return fn(*args, **kwargs)
    decorated_function.__name__ = fn.__name__
    return decorated_function

def convert_funciones_result(result):
    """Convert funciones result to JSON serializable format"""
    funciones = []
    for row in result:
        func = dict(row)
        # Convert hora (timedelta) to string
        if func.get('hora'):
            func['hora'] = str(func['hora'])
        # Convert fecha to string if needed
        if func.get('fecha'):
            func['fecha'] = str(func['fecha'])
        funciones.append(func)
    return funciones


@funciones_bp.route('/', methods=['GET'])
def get_funciones():
    """Get available functions for cartelera (only active movies)"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Join with peliculas to get the movie title
            # Use alias titulo_pelicula for frontend compatibility
            sql = """
                SELECT f.*, p.titulo as titulo_pelicula, p.imagen_url 
                FROM funciones f 
                JOIN peliculas p ON f.pelicula_id = p.id
                WHERE f.estado = 'disponible' AND p.estado = 'activa'
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            # Convert to JSON serializable format
            return jsonify(convert_funciones_result(result)), 200
    except Exception as e:
        print(f"DEBUG - Error getting funciones: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@funciones_bp.route('/all', methods=['GET'])
def get_all_funciones():
    """Get ALL functions for admin panel (including inactive movies)"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get all functions regardless of estado for admin
            sql = """
                SELECT f.*, p.titulo as titulo_pelicula, p.imagen_url 
                FROM funciones f 
                JOIN peliculas p ON f.pelicula_id = p.id
                ORDER BY f.fecha DESC, f.hora DESC
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            # Convert to JSON serializable format
            return jsonify(convert_funciones_result(result)), 200
    except Exception as e:
        print(f"DEBUG - Error getting all funciones: {str(e)}")
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


@funciones_bp.route('/<int:funcion_id>/asientos/<int:asiento_id>', methods=['PUT'])
def update_asiento_estado(funcion_id, asiento_id):
    """Admin endpoint to update seat status for a specific function"""
    data = request.json
    nuevo_estado = data.get('estado')  # 'disponible', 'ocupado', 'mantenimiento'
    
    if nuevo_estado not in ['disponible', 'ocupado', 'mantenimiento']:
        return jsonify({"error": "Estado inválido. Use: disponible, ocupado, o mantenimiento"}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar que la función existe
            cursor.execute("SELECT id FROM funciones WHERE id = %s", (funcion_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Función no encontrada"}), 404
            
            # Verificar que el asiento existe
            cursor.execute("SELECT id FROM asientos WHERE id = %s", (asiento_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Asiento no encontrado"}), 404
            
            # Si el estado es 'ocupado', crear un registro en detalle_tiquete
            if nuevo_estado == 'ocupado':
                # Crear un tiquete de "mantenimiento" para el admin
                import uuid
                codigo = f"ADM-{str(uuid.uuid4())[:6].upper()}"
                cursor.execute("""
                    INSERT INTO tiquetes (codigo, usuario_id, funcion_id, total, estado)
                    VALUES (%s, NULL, %s, 0, 'usado')
                """, (codigo, funcion_id))
                tiquete_id = cursor.lastrowid
                
                # Marcar el asiento como ocupado
                cursor.execute("""
                    INSERT INTO detalle_tiquete (tiquete_id, funcion_id, asiento_id, precio_unitario)
                    VALUES (%s, %s, %s, 0)
                """, (tiquete_id, funcion_id, asiento_id))
            
            # Si el estado es 'disponible' o 'mantenimiento', liberar el asiento
            elif nuevo_estado in ['disponible', 'mantenimiento']:
                # Eliminar cualquier reserva existente
                cursor.execute("""
                    DELETE FROM detalle_tiquete 
                    WHERE funcion_id = %s AND asiento_id = %s
                """, (funcion_id, asiento_id))
                
                # También eliminar tiquetes huérfanos (total 0 y estado usado)
                cursor.execute("""
                    DELETE FROM tiquetes 
                    WHERE funcion_id = %s AND total = 0 AND estado = 'usado'
                    AND id NOT IN (SELECT DISTINCT tiquete_id FROM detalle_tiquete)
                """, (funcion_id,))
            
            conn.commit()
            return jsonify({
                "message": f"Asiento actualizado a '{nuevo_estado}'",
                "asiento_id": asiento_id,
                "funcion_id": funcion_id,
                "estado": nuevo_estado
            }), 200
            
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@funciones_bp.route('/', methods=['POST'])
# @admin_required  # Temporarily disabled for testing
def create_funcion():
    data = request.json
    pelicula_id = data.get('pelicula_id')
    fecha = data.get('fecha')
    hora = data.get('hora')
    precio = data.get('precio')
    
    # Debug logging
    print(f"DEBUG - Creating function: pelicula_id={pelicula_id}, fecha={fecha}, hora={hora}, precio={precio}")
    
    if not pelicula_id or not fecha or not hora or not precio:
        return jsonify({"error": "Faltan datos requeridos", "details": f"pelicula_id={pelicula_id}, fecha={fecha}, hora={hora}, precio={precio}"}), 400
    
    # Ensure pelicula_id is an integer
    try:
        pelicula_id = int(pelicula_id)
    except (ValueError, TypeError):
        return jsonify({"error": "ID de película inválido"}), 400
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verify pelicula exists
            cursor.execute("SELECT id, titulo FROM peliculas WHERE id = %s", (pelicula_id,))
            pelicula = cursor.fetchone()
            if not pelicula:
                return jsonify({"error": f"Película con ID {pelicula_id} no existe"}), 400
            
            print(f"DEBUG - Pelicula found: {pelicula}")
            
            cursor.execute("""
                INSERT INTO funciones (pelicula_id, fecha, hora, sala, precio, estado)
                VALUES (%s, %s, %s, %s, %s, 'disponible')
            """, (pelicula_id, fecha, hora, data.get('sala', 'Sala 1'), precio))
            conn.commit()
            print(f"DEBUG - Function created successfully")
            return jsonify({"message": "Funcion creada", "id": cursor.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        print(f"DEBUG - Error creating function: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@funciones_bp.route('/<int:id>', methods=['GET'])
def get_funcion(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Obtener función específica con info de la película
            sql = """
                SELECT f.*, p.titulo, p.imagen_url, p.genero, p.clasificacion
                FROM funciones f 
                JOIN peliculas p ON f.pelicula_id = p.id
                WHERE f.id = %s
            """
            cursor.execute(sql, (id,))
            funcion = cursor.fetchone()
            if funcion:
                return jsonify(funcion), 200
            return jsonify({"error": "Funcion no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@funciones_bp.route('/<int:id>', methods=['PUT'])
# @admin_required  # Temporarily disabled for testing
def update_funcion(id):
    data = request.json
    
    # Validar que al menos un campo esté presente
    campos = ['pelicula_id', 'fecha', 'hora', 'sala', 'precio', 'estado']
    if not any(data.get(campo) for campo in campos):
        return jsonify({"error": "Debe proporcionar al menos un campo para actualizar"}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar que la función existe
            cursor.execute("SELECT id FROM funciones WHERE id = %s", (id,))
            if not cursor.fetchone():
                return jsonify({"error": "Funcion no encontrada"}), 404
            
            # Si se cambia pelicula_id, verificar que existe
            if data.get('pelicula_id'):
                cursor.execute("SELECT id FROM peliculas WHERE id = %s", (data.get('pelicula_id'),))
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
                UPDATE funciones 
                SET {', '.join(updates)}
                WHERE id = %s
            """, tuple(valores))
            conn.commit()
            
            return jsonify({"message": "Funcion actualizada correctamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@funciones_bp.route('/<int:id>', methods=['DELETE'])
# @admin_required  # Temporarily disabled for testing
def delete_funcion(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar que la función existe
            cursor.execute("SELECT id, estado FROM funciones WHERE id = %s", (id,))
            funcion = cursor.fetchone()
            if not funcion:
                return jsonify({"error": "Funcion no encontrada"}), 404
            
            # Verificar si ya está cancelada
            if funcion['estado'] == 'cancelada':
                return jsonify({"error": "La funcion ya esta cancelada"}), 400
            
            # Verificar si hay tiquetes comprados (no permitir cancelar si hay ventas)
            cursor.execute("""
                SELECT id FROM detalle_tiquete 
                WHERE funcion_id = %s
            """, (id,))
            if cursor.fetchone():
                return jsonify({"error": "No se puede cancelar la funcion porque ya hay tiquetes vendidos"}), 400
            
            # Cambiar estado a cancelada (no eliminar físicamente)
            cursor.execute("""
                UPDATE funciones 
                SET estado = 'cancelada' 
                WHERE id = %s
            """, (id,))
            conn.commit()
            
            return jsonify({"message": "Funcion cancelada correctamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
