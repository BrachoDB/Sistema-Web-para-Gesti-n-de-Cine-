from flask import Blueprint, jsonify, request
from db import get_db_connection
import uuid
from datetime import datetime, timedelta


# Importamos el servicio de email con seguridad manejando errores de importacion
try:
    from services.email_service import EmailService
except ImportError as e:
    print(f"ADVERTENCIA: No se pudo cargar EmailService en tiquetes.py: {e}")
    EmailService = None

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
            # Obtenemos detalles de la funcion y la pelicula para el correo
            cursor.execute("""
                SELECT f.precio, f.fecha, f.hora, p.titulo 
                FROM funciones f
                JOIN peliculas p ON f.pelicula_id = p.id
                WHERE f.id = %s AND f.estado = 'disponible'
            """, (funcion_id,))
            funcion = cursor.fetchone()
            
            if not funcion:
                return jsonify({"error": "Funcion no encontrada o no disponible"}), 404
                
            # Datos para el tiquete y el email
            precio_unitario = funcion['precio']
            fecha_str = str(funcion['fecha'])
            hora_str = str(funcion['hora'])
            titulo_pelicula = funcion['titulo']
            total = len(asientos) * precio_unitario
            
            # Comienza transaccion
            conn.begin()
            
            # Verificamos disponibilidad de asientos
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
                
            # Crear tiquete
            codigo = str(uuid.uuid4())[:8].upper()
            cursor.execute("""
                INSERT INTO tiquetes (codigo, usuario_id, funcion_id, total) 
                VALUES (%s, %s, %s, %s)
            """, (codigo, usuario_id, funcion_id, total))
            
            tiquete_id = cursor.lastrowid
            
            # Insertar detalles
            for asiento_id in asientos:
                cursor.execute("""
                    INSERT INTO detalle_tiquete (tiquete_id, funcion_id, asiento_id, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (tiquete_id, funcion_id, asiento_id, precio_unitario))
                
            conn.commit()
            
            # ENVIO DE EMAIL (SI HAY USUARIO)
            if usuario_id and EmailService:
                try:
                    cursor.execute("SELECT email, nombre FROM usuarios WHERE id = %s", (usuario_id,))
                    user_data = cursor.fetchone()
                    if user_data:
                        EmailService.send_ticket_confirmation(
                            user_email=user_data['email'],
                            user_name=user_data['nombre'],
                            ticket_code=codigo,
                            movie_title=titulo_pelicula,
                            date=fecha_str,
                            time=hora_str,
                            total=total
                        )
                except Exception as email_err:
                    print(f"Error al procesar email: {email_err}")

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
            # Obtenemos el tiquete con datos de la función y la duración de la película
            cursor.execute("""
                SELECT t.id, t.estado, f.fecha, f.hora, p.duracion 
                FROM tiquetes t
                JOIN funciones f ON t.funcion_id = f.id
                JOIN peliculas p ON f.pelicula_id = p.id
                WHERE t.codigo = %s
            """, (codigo,))
            tiquete = cursor.fetchone()
            
            if not tiquete:
                return jsonify({"estado": "Invalido", "mensaje": "Código no encontrado"}), 200
                
            if tiquete['estado'] == 'usado':
                return jsonify({
                    "estado": "Usado", 
                    "mensaje": "Este tiquete ya fue utilizado",
                    "error": "Este tiquete ya fue utilizado"
                }), 403
            
            # --- VALIDACIÓN DE TIEMPO ---
            # Combinamos fecha y hora de la función
            show_date = tiquete['fecha']
            show_time = tiquete['hora']
            
            # Nota: tiquete['hora'] suele ser un objeto timedelta en pymysql si la columna es TIME
            if isinstance(show_time, timedelta):
                show_start = datetime.combine(show_date, (datetime.min + show_time).time())
            else:
                show_start = datetime.combine(show_date, show_time)
                
            # Ajustamos la hora actual al desfase de Colombia (UTC-5) 
            # ya que el servidor (Vercel) opera en UTC.
            now = datetime.now() - timedelta(hours=5)
            
            # 1. ¿Es demasiado temprano? (Más de 15 minutos antes)
            if now < (show_start - timedelta(minutes=15)):
                minutos_faltantes = int((show_start - now).total_seconds() / 60)
                msg = f"Demasiado temprano. Faltan {minutos_faltantes} minutos para la función."
                return jsonify({
                    "estado": "Temprano", 
                    "mensaje": msg,
                    "error": msg
                }), 403
            
            # 2. ¿La función ya terminó? (Inicio + Duración)
            show_end = show_start + timedelta(minutes=tiquete['duracion'])
            if now > show_end:
                msg = "La función ya ha terminado."
                return jsonify({
                    "estado": "Finalizada", 
                    "mensaje": msg,
                    "error": msg
                }), 403
                
            # --- PROCESAR VALIDACIÓN ---
            if tiquete['estado'] == 'valido':
                cursor.execute("UPDATE tiquetes SET estado = 'usado' WHERE id = %s", (tiquete['id'],))
                conn.commit()
                return jsonify({"estado": "Valido", "mensaje": "Acceso concedido"}), 200
                
            return jsonify({
                "estado": "Invalido", 
                "mensaje": "Tiquete no válido",
                "error": "Tiquete no válido"
            }), 403

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
