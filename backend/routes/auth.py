from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validar datos requeridos
    if not data:
        return jsonify({'error': 'No se recibieron datos'}), 400
    
    nombre = data.get('nombre', '').strip()
    email = data.get('email', '').strip().lower()
    contrasena = data.get('contrasena', '')
    
    if not nombre or not email or not contrasena:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400
    
    if len(contrasena) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
    
    # Verificar que el email no exista
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
            if cursor.fetchone():
                return jsonify({'error': 'El email ya está registrado'}), 400
            
            # Crear usuario con rol 'cliente'
            hashed_password = generate_password_hash(contrasena)
            cursor.execute(
                'INSERT INTO usuarios (nombre, email, contrasena, rol) VALUES (%s, %s, %s, %s)',
                (nombre, email, hashed_password, 'cliente')
            )
            conn.commit()
            
            user_id = cursor.lastrowid
            
            # Crear token JWT
            access_token = create_access_token(
                identity=str(user_id), 
                additional_claims={'rol': 'cliente'}
            )
            
            return jsonify({
                'message': 'Usuario registrado exitosamente',
                'token': access_token,
                'user_id': user_id,
                'nombre': nombre,
                'rol': 'cliente'
            }), 201
    except Exception as e:
        return jsonify({'error': f'Error al registrar usuario: {str(e)}'}), 500
    finally:
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se recibieron datos'}), 400
    
    email = data.get('email', '').strip().lower()
    contrasena = data.get('contrasena', '')
    
    if not email or not contrasena:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            if not user or not check_password_hash(user['contrasena'], contrasena):
                return jsonify({'error': 'Credenciales inválidas'}), 401
            
            # Crear token JWT con la identidad del usuario
            access_token = create_access_token(
                identity=str(user['id']), 
                additional_claims={'rol': user['rol']}
            )
            
            return jsonify({
                'message': 'Login exitoso',
                'token': access_token,
                'user_id': user['id'],
                'nombre': user['nombre'],
                'rol': user['rol']
            }), 200
    except Exception as e:
        return jsonify({'error': f'Error al iniciar sesión: {str(e)}'}), 500
    finally:
        conn.close()

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, nombre, email, rol, fecha_creacion FROM usuarios WHERE id = %s', (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    return jsonify({'error': 'Usuario no encontrado'}), 404
                
                return jsonify(user), 200
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': f'Error al obtener usuario: {str(e)}'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Permite al usuario cambiar su contraseña"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se recibieron datos'}), 400
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'La contraseña actual y la nueva son requeridas'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'La nueva contraseña debe tener al menos 6 caracteres'}), 400
    
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Verificar contraseña actual
                cursor.execute('SELECT contrasena FROM usuarios WHERE id = %s', (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    return jsonify({'error': 'Usuario no encontrado'}), 404
                
                if not check_password_hash(user['contrasena'], current_password):
                    return jsonify({'error': 'Contraseña actual incorrecta'}), 401
                
                # Actualizar contraseña
                hashed_new_password = generate_password_hash(new_password)
                cursor.execute(
                    'UPDATE usuarios SET contrasena = %s WHERE id = %s',
                    (hashed_new_password, user_id)
                )
                conn.commit()
                
                return jsonify({'message': 'Contraseña actualizada correctamente'}), 200
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': f'Error al cambiar contraseña: {str(e)}'}), 500


@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Actualizar perfil del usuario"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se recibieron datos'}), 400
    
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Actualizar nombre
                nombre = data.get('nombre')
                if nombre:
                    cursor.execute(
                        'UPDATE usuarios SET nombre = %s WHERE id = %s',
                        (nombre, user_id)
                    )
                
                conn.commit()
                
                # Obtener usuario actualizado
                cursor.execute('SELECT id, nombre, email, rol FROM usuarios WHERE id = %s', (user_id,))
                user = cursor.fetchone()
                
                return jsonify({
                    'message': 'Perfil actualizado correctamente',
                    'user': user
                }), 200
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': f'Error al actualizar perfil: {str(e)}'}), 500
