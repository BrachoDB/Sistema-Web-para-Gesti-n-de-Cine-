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
            data = {
                'Messages': [
                    {
                        "From": {"Email": Config.MAILJET_SENDER, "Name": "CineMax"},
                        "To": [{"Email": user_email, "Name": user_name}],
                        "Subject": "Bienvenido a CineMax!",
                        "HTMLPart": f"<h3>Hola {user_name}!</h3><p>Gracias por unirte.</p>"
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
            data = {
                'Messages': [
                    {
                        "From": {"Email": Config.MAILJET_SENDER, "Name": "CineMax"},
                        "To": [{"Email": user_email, "Name": user_name}],
                        "Subject": f"Tiquete: {movie_title}",
                        "HTMLPart": f"<h3>Reserva Confirmada!</h3><p>Codigo: {ticket_code}</p><img src='cid:tqr' width='200'/>",
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
            data = {
                'Messages': [
                    {
                        "From": {"Email": Config.MAILJET_SENDER, "Name": "CineMax"},
                        "To": [{"Email": user_email, "Name": user_name}],
                        "Subject": "Recuperar Contrasena",
                        "HTMLPart": f"<p>Hola {user_name}, clic: <a href='{url}'>Reset</a></p>"
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

