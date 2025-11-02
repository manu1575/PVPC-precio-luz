import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

# === Variables de entorno (GitHub Secrets) ===
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', '')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

JSON_PATH = "outputs/pvpc.json"

if not EMAIL_USER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
    print("⚠️ Notificación desactivada: faltan credenciales de correo.")
    exit(0)

if not os.path.exists(JSON_PATH):
    print(f"❌ No se encontró {JSON_PATH}. No se enviará ningún correo.")
    exit(1)

# === Leer fecha del JSON ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    datos = json.load(f)

fecha_publicacion = datos.get("fecha_publicacion")
if not fecha_publicacion:
    print("⚠️ No se encontró 'fecha_publicacion' en el JSON. No se enviará el correo.")
    exit(1)

fecha_dt = datetime.strptime(fecha_publicacion, "%Y-%m-%d")
pdf_filename = f"outputs/pvpc_{fecha_dt.strftime('%Y%m%d')}.pdf"

if not os.path.exists(pdf_filename):
    print(f"❌ PDF {pdf_filename} no encontrado. No se enviará el correo.")
    exit(1)

# === Crear mensaje con adjunto ===
destinatarios = [x.strip() for x in EMAIL_RECEIVER.split(",") if x.strip()]

msg = MIMEMultipart()
msg["From"] = EMAIL_USER
msg["To"] = ", ".join(destinatarios)
msg["Subject"] = f"Informe PVPC diario – {fecha_dt.strftime('%d/%m/%Y')}"
body = f"Adjunto se envía el informe diario de PVPC correspondiente al {fecha_dt.strftime('%d/%m/%Y')}."
msg.attach(MIMEText(body, "plain"))

with open(pdf_filename, "rb") as f:
    part = MIMEApplication(f.read(), Name=os.path.basename(pdf_filename))
part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_filename)}"'
msg.attach(part)

# === Enviar correo ===
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, destinatarios, msg.as_string())
    print(f"📧 Correo enviado correctamente a: {', '.join(destinatarios)}")
except Exception as e:
    print(f"❌ Error al enviar correo: {e}")
    exit(1)
