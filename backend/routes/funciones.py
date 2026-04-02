from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from db import get_db_connection
from datetime import datetime, timedelta

funciones_bp = Blueprint('funciones', __name__)


def admin_required(fn):
    """Decorador para verificar que el usuario es administrador"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('rol') != 'admin':
            return jsonify({'error': 'Acceso no autorizado. Se requiere rol de administrador'}), 403
        return fn(*args, **kwargs)
    decorated_function.__name__ = fn.__name__
    return decorated_function

def convert_funciones_result(result):
    """Convert funciones result to JSON serializable format"""
    funciones = []
    for row in result:
        funciones.append(convert_single_funcion(row))
    return funciones


def convert_single_funcion(row):
    """Convert a single function row to JSON serializable format"""
    if not row:
        return None
    func = dict(row)
    # Convert hora (timedelta) to string
    if func.get('hora') is not None:
        func['hora'] = str(func['hora'])
    # Convert fecha to string if needed
    if func.get('fecha') is not None:
        func['fecha'] = str(func['fecha'])
    # Convert precio (Decimal) to float if needed
    if func.get('precio') is not None:
        func['precio'] = float(func['precio'])
    return func


def check_overlap(cursor, sala, fecha, hora_str, pelicula_id, exclude_id=None):
    """
    Verifica si hay traslape de horarios en la misma sala y fecha.
    Incluye un margen de 20 minutos para limpieza.
    """
    # 1. Obtener duración de la película propuesta
    cursor.execute("SELECT duracion FROM peliculas WHERE id = %s", (pelicula_id,))
    pelicula = cursor.fetchone()
    if not pelicula:
        return "Película no encontrada"
    
    duracion_nueva = pelicula['duracion']
    
    # Convertir fecha y hora a objetos datetime para cálculos
    if isinstance(fecha, str):
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    else:
        fecha_obj = fecha
        
    hora_obj = datetime.strptime(hora_str[:5], '%H:%M').time()
    inicio_nuevo = datetime.combine(fecha_obj, hora_obj)
    fin_nuevo = inicio_nuevo + timedelta(minutes=duracion_nueva + 20)  # +20 min limpieza
    
    # 2. Consultar funciones existentes en la misma sala y fecha
    sql = """
        SELECT f.id, f.hora, p.duracion, p.titulo
        FROM funciones f
        JOIN peliculas p ON f.pelicula_id = p.id
        WHERE f.sala = %s AND f.fecha = %s AND f.estado != 'cancelada'
    """
    params = [sala, fecha_obj]
    if exclude_id:
        sql += " AND f.id != %s"
        params.append(exclude_id)
        
    cursor.execute(sql, tuple(params))
    funciones_dia = cursor.fetchall()
    
    for f in funciones_dia:
        # f['hora'] suele ser un objeto timedelta en pymysql para columnas TIME
        if isinstance(f['hora'], timedelta):
            f_inicio_time = (datetime.min + f['hora']).time()
        else:
            # Por si acaso viene como string
            f_inicio_time = datetime.strptime(str(f['hora'])[:5], '%H:%M').time()
            
        f_inicio = datetime.combine(fecha_obj, f_inicio_time)
        f_fin = f_inicio + timedelta(minutes=f['duracion'] + 20)
        
        # Algoritmo de traslape: (InicioA < FinB) AND (FinA > InicioB)
        if inicio_nuevo < f_fin and fin_nuevo > f_inicio:
            return f"Conflicto de horario: '{f['titulo']}' ocupa la sala de {f_inicio.strftime('%H:%M')} a {f_fin.strftime('%H:%M')} (con limpieza)."
            
    return None


@funciones_bp.route('/', methods=['GET'])
def get_funciones():
    """Get available functions for cartelera (only active movies)"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Join with peliculas to get the movie title
            # Use alias titulo_pelicula for frontend compatibility
            sql = """
                SELECT f.*, p.titulo as titulo_pelicula, p.imagen_url, p.duracion, p.descripcion 
                FROM funciones f 
                JOIN peliculas p ON f.pelicula_id = p.id
                WHERE f.estado IN ('disponible', 'cancelada')
                ORDER BY f.fecha ASC, f.hora ASC
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
                SELECT f.*, p.titulo as titulo_pelicula, p.imagen_url, p.duracion, p.descripcion 
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
            # Retorna el estado real del asiento:
            # - 'ocupado' si hay un registro en detalle_tiquete O el asiento está marcado como 'ocupado'
            # - 'mantenimiento' si el asiento tiene ese estado en la tabla asientos
            # - 'disponible' en cualquier otro caso
            # Agregamos 'is_sold' para que el frontend sepa si puede "Liberarlo"
            sql = """
                SELECT a.*, 
                CASE 
                    WHEN dt.id IS NOT NULL THEN 'ocupado'
                    WHEN a.estado = 'ocupado' THEN 'ocupado'
                    WHEN a.estado = 'mantenimiento' THEN 'mantenimiento'
                    ELSE 'disponible' 
                END as estado_funcion,
                CASE WHEN dt.id IS NOT NULL THEN 1 ELSE 0 END as is_sold
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
    nuevo_estado = data.get('estado')  # 'disponible', 'mantenimiento', 'ocupado'
    liberar_vendido = data.get('liberar_vendido', False)
    
    if nuevo_estado not in ['disponible', 'mantenimiento', 'ocupado']:
        return jsonify({"error": "Estado inválido. Use: disponible, mantenimiento o ocupado"}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar que la función existe
            cursor.execute("SELECT id FROM funciones WHERE id = %s", (funcion_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Función no encontrada"}), 404
            
            # Verificar que el asiento existe
            cursor.execute("SELECT id, estado FROM asientos WHERE id = %s", (asiento_id,))
            asiento = cursor.fetchone()
            if not asiento:
                return jsonify({"error": "Asiento no encontrado"}), 404
            
            # Verificar si está vendido
            cursor.execute("""
                SELECT id FROM detalle_tiquete 
                WHERE funcion_id = %s AND asiento_id = %s
            """, (funcion_id, asiento_id))
            detalle = cursor.fetchone()
            
            if detalle:
                if liberar_vendido:
                    # Liberar asiento vendido (eliminar detalle)
                    # NOTA: Esto no ajusta el 'total' del tiquete padre, 
                    # en un sistema real se debería manejar una nota de crédito o devolución.
                    cursor.execute("DELETE FROM detalle_tiquete WHERE id = %s", (detalle['id'],))
                    print(f"DEBUG - Asiento {asiento_id} liberado (venta eliminada) en funcion {funcion_id}")
                else:
                    return jsonify({"error": "No se puede cambiar el estado: el asiento está vendido. Use 'liberar_vendido: true' para forzar."}), 400
            
            # Actualizar el estado del asiento directamente en la tabla asientos
            cursor.execute("""
                UPDATE asientos SET estado = %s WHERE id = %s
            """, (nuevo_estado, asiento_id))
            
            conn.commit()
            return jsonify({
                "message": f"Asiento actualizado a '{nuevo_estado}'",
                "asiento_id": asiento_id,
                "funcion_id": funcion_id,
                "estado": nuevo_estado,
                "liberado": liberar_vendido if detalle else False
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
            
            # --- NUEVA VALIDACIÓN DE TRASLAPE ---
            error_config = check_overlap(cursor, data.get('sala', 'Sala 1'), fecha, hora, pelicula_id)
            if error_config:
                return jsonify({"error": error_config}), 400
            
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
                return jsonify(convert_single_funcion(funcion)), 200
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
            
            # Si se cambia horario, sala o película, re-validar traslape
            if any(campo in data for campo in ['fecha', 'hora', 'sala', 'pelicula_id']):
                # Obtener valores actuales para completar la validación
                cursor.execute("SELECT fecha, hora, sala, pelicula_id FROM funciones WHERE id = %s", (id,))
                actual = cursor.fetchone()
                
                v_fecha = data.get('fecha', actual['fecha'])
                v_hora = data.get('hora', str(actual['hora']))
                v_sala = data.get('sala', actual['sala'])
                v_peli = data.get('pelicula_id', actual['pelicula_id'])
                
                error_config = check_overlap(cursor, v_sala, v_fecha, v_hora, v_peli, exclude_id=id)
                if error_config:
                    return jsonify({"error": error_config}), 400

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
            
            # Verificar si hay tiquetes comprados (no permitir eliminar si hay ventas)
            cursor.execute("""
                SELECT id FROM detalle_tiquete 
                WHERE funcion_id = %s
            """, (id,))
            if cursor.fetchone():
                return jsonify({"error": "No se puede eliminar la funcion porque ya hay tiquetes vendidos. Se recomienda cancelarla."}), 400
            
            # Eliminar físicamente
            cursor.execute("DELETE FROM funciones WHERE id = %s", (id,))
            conn.commit()
            
            return jsonify({"message": "Funcion eliminada correctamente"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
