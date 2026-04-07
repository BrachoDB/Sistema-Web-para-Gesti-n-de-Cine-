import base64
from io import BytesIO
import os

# Intentamos importar librerías externas. Si fallan en servidor, no tumbamos el backend.
try:
    import qrcode
except ImportError:
    print("⚠ ¡ATENCIÓN! La librería 'qrcode' no está instalada. Los tiquetes no incluirán QR por correo.")
    qrcode = None

try:
    from mailjet_rest import Client
except ImportError as e:
    print(f"⚠ ¡ATENCIÓN! La librería 'mailjet-rest' no está instalada: {e}")
    Client = None

from config import Config

class EmailService:
    """Servicio para manejo de correos electrónicos con Mailjet"""
    
    @staticmethod
    def _get_client():
        return Client(auth=(Config.MAILJET_API_KEY, Config.MAILJET_API_SECRET), version='v3.1')

    @staticmethod
    def send_welcome_email(user_email, user_name):
        """Envía un correo de bienvenida a un nuevo usuario"""
        if not Config.MAILJET_API_KEY or not Config.MAILJET_API_SECRET:
            print("⚠ Mailjet no configurado. El correo no se envió.")
            return False

        client = EmailService._get_client()
        data = {
            'Messages': [
                {
                    "From": {"Email": Config.MAILJET_SENDER, "Name": "CineMax Support"},
                    "To": [{"Email": user_email, "Name": user_name}],
                    "Subject": "¡Bienvenido a la Experiencia CineMax!",
                    "HTMLPart": f"""
                        <div style="font-family: Arial, sans-serif; background: #0c0d14; color: #fff; padding: 40px; border-radius: 12px;">
                            <h1 style="color: #d4a853;">¡Hola {user_name}!</h1>
                            <p style="font-size: 1.1em;">Gracias por unirte a CineMax. Estamos felices de tenerte con nosotros.</p>
                            <p>Ahora puedes reservar tus asientos favoritos para los mejores estrenos.</p>
                            <hr style="border: 0; border-top: 1px solid #333; margin: 25px 0;">
                            <p style="color: #7d7f91; font-size: 0.9em;">Este es un mensaje automático, por favor no respondas.</p>
                        </div>
                    """
                }
            ]
        }
        try:
            result = client.send.create(data=data)
            return result.status_code == 200
        except Exception as e:
            print(f"Error enviando bienvenida: {str(e)}")
            return False

    @staticmethod
    def send_ticket_confirmation(user_email, user_name, ticket_code, movie_title, date, time, total):
        """Envía confirmación de compra con código QR incrustado"""
        if not Config.MAILJET_API_KEY or not Config.MAILJET_API_SECRET:
            print("⚠ Mailjet no configurado. El correo de confirmación no se envió.")
            return False

        # Generar código QR en memoria
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(ticket_code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        client = EmailService._get_client()
        data = {
            'Messages': [
                {
                    "From": {"Email": Config.MAILJET_SENDER, "Name": "CineMax Reservas"},
                    "To": [{"Email": user_email, "Name": user_name}],
                    "Subject": f"Tu Tiquete para: {movie_title} 🎬",
                    "HTMLPart": f"""
                        <div style="font-family: Arial, sans-serif; background: #0c0d14; color: #fff; padding: 30px; border-radius: 12px; border: 1px solid #d4a853;">
                            <h2 style="color: #d4a853; text-align: center;">¡Reserva Confirmada!</h2>
                            <p>Hola {user_name}, aquí tienes los detalles de tu función:</p>
                            
                            <div style="background: #1a1b26; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <p><strong>Película:</strong> {movie_title}</p>
                                <p><strong>Fecha:</strong> {date}</p>
                                <p><strong>Hora:</strong> {time}</p>
                                <p><strong>Total pagado:</strong> ${total}</p>
                                <p style="font-size: 1.2em; color: #d4a853;"><strong>Código: {ticket_code}</strong></p>
                            </div>

                            <p style="text-align: center;">Presenta este código QR en la entrada del cinema:</p>
                            <div style="text-align: center; background: #fff; padding: 20px; display: inline-block; width: 100%; border-radius: 8px;">
                                <img src="cid:ticket_qr" width="200" height="200" alt="Código QR del Tiquete">
                            </div>
                            
                            <p style="margin-top: 25px; font-size: 0.85em; color: #7d7f91; text-align: center;">
                                © 2024 CineMax - La mejor experiencia cinematográfica.
                            </p>
                        </div>
                    """,
                    "InlinedAttachments": [
                        {
                            "ContentType": "image/png",
                            "Filename": "qr.png",
                            "ContentID": "ticket_qr",
                            "Base64Content": qr_base64
                        }
                    ]
                }
            ]
        }
        try:
            result = client.send.create(data=data)
            return result.status_code == 200
        except Exception as e:
            print(f"Error enviando confirmación: {str(e)}")
            return False

    @staticmethod
    def send_password_reset(user_email, user_name, reset_token):
        """Envía enlace para restablecer contraseña"""
        if not Config.MAILJET_API_KEY or not Config.MAILJET_API_SECRET:
            print("⚠ Mailjet no configurado. El correo de recuperación no se envió.")
            return False

        reset_url = f"{Config.FRONTEND_URL}/reset-password.html?token={reset_token}"
        
        client = EmailService._get_client()
        data = {
            'Messages': [
                {
                    "From": {"Email": Config.MAILJET_SENDER, "Name": "CineMax Seguridad"},
                    "To": [{"Email": user_email, "Name": user_name}],
                    "Subject": "Restablecer tu contraseña de CineMax",
                    "HTMLPart": f"""
                        <div style="font-family: Arial, sans-serif; background: #0c0d14; color: #fff; padding: 40px; border-radius: 12px;">
                            <h2 style="color: #d4a853;">Recuperación de Cuenta</h2>
                            <p>Hola {user_name}, recibimos una solicitud para restablecer tu contraseña.</p>
                            <p>Haz clic en el siguiente botón para crear una nueva clave:</p>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{reset_url}" 
                                   style="background: #d4a853; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1em;">
                                   Restablecer Contraseña
                                </a>
                            </div>
                            
                            <p style="color: #7d7f91; font-size: 0.9em;">Si no solicitaste este cambio, puedes ignorar este correo de forma segura. El enlace expirará en 15 minutos.</p>
                            <p style="color: #7d7f91; font-size: 0.8em; margin-top: 20px;">Si el botón no funciona, copia y pega este enlace:<br>{reset_url}</p>
                        </div>
                    """
                }
            ]
        }
        try:
            result = client.send.create(data=data)
            return result.status_code == 200
        except Exception as e:
            print(f"Error enviando reset: {str(e)}")
            return False
