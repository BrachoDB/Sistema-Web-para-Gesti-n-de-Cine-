import base64
import logging
from io import BytesIO
import os

# Configuración del logger
logger = logging.getLogger(__name__)


# Intentamos importar librerias externas. Si fallan en servidor, no tumbamos el backend.
try:
    import qrcode
except ImportError:
    logger.warning("qrcode no esta instalado. La funcionalidad de tickets QR no estara disponible.")
    qrcode = None

try:
    from mailjet_rest import Client
except ImportError as e:
    logger.error(f"mailjet-rest no esta disponible: {e}")
    Client = None


from config import Config

class EmailServiceError(Exception):
    """Excepción base para errores en el servicio de correo."""
    pass

class EmailService:
    @staticmethod
    def _validate_config():
        """Valida que las credenciales de Mailjet estén presentes."""
        if not Config.MAILJET_API_KEY or not Config.MAILJET_API_SECRET:
            logger.error("Faltan MAILJET_API_KEY o MAILJET_API_SECRET en la configuración.")
            return False
        if not Config.MAILJET_SENDER:
            logger.error("Falta MAILJET_SENDER en la configuración.")
            return False
        if not Client:
            logger.error("El cliente de Mailjet no pudo ser inicializado (falta la librería).")
            return False
        return True

    @staticmethod
    def _get_client():
        if not EmailService._validate_config():
            raise EmailServiceError("Error de configuración en EmailService")
        return Client(auth=(Config.MAILJET_API_KEY, Config.MAILJET_API_SECRET), version='v3.1')

    @staticmethod
    def send_welcome_email(user_email, user_name):
        try:
            client = EmailService._get_client()
            html_content = f"""
            <div style="background-color: #07080c; color: #ecedf2; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 40px 20px; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #0c0d14; border: 1px solid #d4a85333; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                    <div style="background: linear-gradient(135deg, #d4a853, #c49540); padding: 30px; text-align: center;">
                        <h1 style="margin: 0; color: #0c0d14; font-size: 28px; font-weight: 800; letter-spacing: -1px;">CineMax</h1>
                    </div>
                    <div style="padding: 40px; text-align: center;">
                        <h2 style="color: #ffffff; margin-bottom: 20px;">¡Bienvenido, {user_name}!</h2>
                        <p style="color: #7d7f91; font-size: 16px; margin-bottom: 30px;">Estamos encantados de que te hayas unido a nuestra comunidad. Prepárate para vivir la mejor experiencia cinematográfica con la última tecnología y el confort que mereces.</p>
                        <a href="{Config.FRONTEND_URL}" style="display: inline-block; padding: 14px 30px; background-color: #d4a853; color: #0c0d14; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 16px;">Explorar Cartelera</a>
                    </div>
                    <div style="background-color: #111219; padding: 20px; text-align: center; border-top: 1px solid #ffffff0a;">
                        <p style="color: #484a5a; font-size: 12px; margin: 0;">&copy; 2026 CineMax. Todos los derechos reservados.</p>
                    </div>
                </div>
            </div>
            """
            data = {
                'Messages': [
                    {
                        "From": {"Email": Config.MAILJET_SENDER, "Name": "CineMax"},
                        "To": [{"Email": user_email, "Name": user_name}],
                        "Subject": "¡Bienvenido a CineMax!",
                        "HTMLPart": html_content
                    }
                ]
            }
            result = client.send.create(data=data)
            if result.status_code == 200:
                logger.info(f"Correo de bienvenida enviado a {user_email}")
                return True
            else:
                logger.error(f"Error Mailjet al enviar bienvenida a {user_email}: {result.status_code} - {result.json()}")
                return False
        except EmailServiceError as e:
            logger.warning(f"No se pudo enviar correo de bienvenida: {str(e)}")
            return False
        except Exception as e:
            logger.exception(f"Error inesperado al enviar correo de bienvenida a {user_email}: {str(e)}")
            return False



    @staticmethod
    def send_ticket_confirmation(user_email, user_name, ticket_code, movie_title, date, time, total):
        try:
            if not qrcode:
                logger.error("No se puede enviar confirmación de ticket: qrcode no instalado.")
                return False
                
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(ticket_code)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode()

            client = EmailService._get_client()
            html_content = f"""
            <div style="background-color: #07080c; color: #ecedf2; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 40px 20px; line-height: 1.6;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #0c0d14; border: 1px solid #d4a85333; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                    <div style="background: linear-gradient(135deg, #d4a853, #c49540); padding: 25px; text-align: center;">
                        <h2 style="margin: 0; color: #0c0d14; font-size: 22px; font-weight: 800;">RESERVA CONFIRMADA</h2>
                    </div>
                    <div style="padding: 30px;">
                        <p style="color: #7d7f91; font-size: 14px; margin-bottom: 20px; text-align: center;">¡Hola {user_name}! Tu tiquete digital está listo.</p>
                        
                        <div style="background-color: #111219; border: 1px dashed #d4a85366; border-radius: 12px; padding: 20px; margin-bottom: 25px;">
                            <h3 style="color: #d4a853; margin: 0 0 15px 0; font-size: 18px; text-align: center; border-bottom: 1px solid #ffffff0a; padding-bottom: 10px;">{movie_title}</h3>
                            <table style="width: 100%; color: #ecedf2; font-size: 14px;">
                                <tr><td style="color: #7d7f91; padding: 5px 0;">Fecha:</td><td style="text-align: right; font-weight: 600;">{date}</td></tr>
                                <tr><td style="color: #7d7f91; padding: 5px 0;">Hora:</td><td style="text-align: right; font-weight: 600;">{time}</td></tr>
                                <tr><td style="color: #7d7f91; padding: 5px 0;">Código:</td><td style="text-align: right; font-weight: 700; color: #d4a853;">{ticket_code}</td></tr>
                                <tr><td style="color: #7d7f91; padding: 15px 0 5px 0; border-top: 1px solid #ffffff0a;">Total:</td><td style="text-align: right; padding-top: 15px; font-weight: 700; font-size: 18px; color: #ffffff;">${total}</td></tr>
                            </table>
                        </div>

                        <div style="text-align: center; background-color: #ffffff; padding: 20px; border-radius: 12px; margin-top: 10px;">
                            <p style="color: #0c0d14; font-size: 12px; margin-bottom: 15px; font-weight: 700;">PRESENTA ESTE CÓDIGO EN LA ENTRADA</p>
                            <img src='cid:tqr' width='180' style="display: block; margin: 0 auto;"/>
                        </div>
                    </div>
                    <div style="background-color: #111219; padding: 15px; text-align: center; border-top: 1px solid #ffffff0a;">
                        <p style="color: #484a5a; font-size: 11px; margin: 0;">Presenta este código 15 minutos antes de la función.</p>
                    </div>
                </div>
            </div>
            """
            data = {
                'Messages': [
                    {
                        "From": {"Email": Config.MAILJET_SENDER, "Name": "CineMax"},
                        "To": [{"Email": user_email, "Name": user_name}],
                        "Subject": f"Tiquete Confirmado: {movie_title}",
                        "HTMLPart": html_content,
                        "InlinedAttachments": [{"ContentType": "image/png", "Filename": "qr.png", "ContentID": "tqr", "Base64Content": qr_base64}]
                    }
                ]
            }
            result = client.send.create(data=data)
            if result.status_code == 200:
                logger.info(f"Confirmación de ticket enviada a {user_email} para {movie_title}")
                return True
            else:
                logger.error(f"Error Mailjet al enviar ticket a {user_email}: {result.status_code} - {result.json()}")
                return False
        except EmailServiceError as e:
            logger.warning(f"No se pudo enviar ticket: {str(e)}")
            return False
        except Exception as e:
            logger.exception(f"Error inesperado al enviar ticket a {user_email}: {str(e)}")
            return False



    @staticmethod
    def send_password_reset(user_email, user_name, reset_token):
        try:
            url = f"{Config.FRONTEND_URL}/reset-password.html?token={reset_token}"
            client = EmailService._get_client()
            html_content = f"""
            <div style="background-color: #07080c; color: #ecedf2; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 40px 20px; line-height: 1.6;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #0c0d14; border: 1px solid #d4a85333; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                    <div style="background-color: #111219; padding: 25px; text-align: center; border-bottom: 1px solid #ffffff0a;">
                        <h2 style="margin: 0; color: #d4a853; font-size: 20px; font-weight: 800; letter-spacing: -0.5px;">CineMax</h2>
                    </div>
                    <div style="padding: 40px; text-align: center;">
                        <h3 style="color: #ffffff; margin-bottom: 20px;">Recuperar Contraseña</h3>
                        <p style="color: #7d7f91; font-size: 15px; margin-bottom: 30px;">Hola {user_name}, hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el siguiente botón para continuar:</p>
                        <a href="{url}" style="display: inline-block; padding: 14px 30px; background-color: #d4a853; color: #0c0d14; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 16px;">Restablecer Contraseña</a>
                        <p style="color: #484a5a; font-size: 13px; margin-top: 30px;">Si no solicitaste este cambio, puedes ignorar este correo con seguridad.</p>
                    </div>
                    <div style="background-color: #111219; padding: 15px; text-align: center;">
                        <p style="color: #333; font-size: 10px; margin: 0;">Este enlace expirará pronto por tu seguridad.</p>
                    </div>
                </div>
            </div>
            """
            data = {
                'Messages': [
                    {
                        "From": {"Email": Config.MAILJET_SENDER, "Name": "CineMax"},
                        "To": [{"Email": user_email, "Name": user_name}],
                        "Subject": "Recuperar Contraseña - CineMax",
                        "HTMLPart": html_content
                    }
                ]
            }
            result = client.send.create(data=data)
            if result.status_code == 200:
                logger.info(f"Correo de recuperación enviado a {user_email}")
                return True
            else:
                logger.error(f"Error Mailjet al enviar recuperación a {user_email}: {result.status_code} - {result.json()}")
                return False
        except EmailServiceError as e:
            logger.warning(f"No se pudo enviar recuperación de contraseña: {str(e)}")
            return False
        except Exception as e:
            logger.exception(f"Error inesperado al enviar recuperación a {user_email}: {str(e)}")
            return False


