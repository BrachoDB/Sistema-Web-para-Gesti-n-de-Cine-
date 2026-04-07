import base64
from io import BytesIO
import os

# Intentamos importar librerias externas. Si fallan en servidor, no tumbamos el backend.
try:
    import qrcode
except ImportError:
    print("ATENCION: qrcode no esta instalado.")
    qrcode = None

try:
    from mailjet_rest import Client
except ImportError as e:
    print(f"ATENCION: mailjet-rest no esta disponible: {e}")
    Client = None

from config import Config

class EmailService:
    @staticmethod
    def _get_client():
        return Client(auth=(Config.MAILJET_API_KEY, Config.MAILJET_API_SECRET), version='v3.1')

    @staticmethod
    def send_welcome_email(user_email, user_name):
        if not Config.MAILJET_API_KEY or not Config.MAILJET_API_SECRET or not Client:
            return False
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
        try:
            result = client.send.create(data=data)
            return result.status_code == 200
        except:
            return False

    @staticmethod
    def send_ticket_confirmation(user_email, user_name, ticket_code, movie_title, date, time, total):
        if not Config.MAILJET_API_KEY or not Config.MAILJET_API_SECRET or not Client or not qrcode:
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
        try:
            result = client.send.create(data=data)
            return result.status_code == 200
        except:
            return False

    @staticmethod
    def send_password_reset(user_email, user_name, reset_token):
        if not Config.MAILJET_API_KEY or not Config.MAILJET_API_SECRET or not Client:
            return False
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
        try:
            result = client.send.create(data=data)
            return result.status_code == 200
        except:
            return False
