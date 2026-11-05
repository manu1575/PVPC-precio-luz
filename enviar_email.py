import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

# === 🔐 Variables de entorno (desde GitHub Secrets) ===
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER", "")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))

JSON_PATH = "outputs/pvpc.json"

# === 🧩 Verificación de credenciales ===
if not EMAIL_USER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
    print("⚠️ Envío de correo desactivado: faltan credenciales de correo.")
    exit(0)

if not os.path.exists(JSON_PATH):
    print(f"❌ No se encontró el archivo {JSON_PATH}. No se enviará ningún correo.")
    exit(1)

# === 📅 Leer JSON para determinar la fecha del informe ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    datos = json.load(f)

fecha_publicacion = datos.get("fecha_publicacion")
if not fecha_publicacion:
    print("⚠️ No se encontró 'fecha_publicacion' en el JSON. No se enviará el correo.")
    exit(1)

fecha_dt = datetime.strptime(fecha_publicacion, "%Y-%m-%d")
pdf_filename = f"outputs/pvpc_{fecha_dt.strftime('%Y%m%d')}.pdf"

if not os.path.exists(pdf_filename):
    print(f"❌ No se encontró el archivo PDF {pdf_filename}. No se enviará el correo.")
    exit(1)

# === 📧 Preparar cuerpo y adjunto del mensaje ===
destinatarios = [x.strip() for x in EMAIL_RECEIVER.split(",") if x.strip()]
if not destinatarios:
    print("⚠️ No se encontraron destinatarios válidos en EMAIL_RECEIVER.")
    exit(0)

body = (
    f"Estimado/a destinatario/a,\n\n"
    f"Adjunto se envía el informe diario del PVPC correspondiente al día "
    f"{fecha_dt.strftime('%d/%m/%Y')}.\n\n"
    "Este mensaje ha sido enviado automáticamente por el sistema de informes diarios de precios eléctricos.\n\n"
    "Atentamente,\n"
    "Sistema Automatizado de Informes PVPC"
)

# === 📤 Envío individual a cada destinatario ===
enviados = 0
fallidos = 0

for destinatario in destinatarios:
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario
    msg["Subject"] = f"Informe diario PVPC – {fecha_dt.strftime('%d/%m/%Y')}"
    msg.attach(MIMEText(body, "plain"))

    # Adjuntar PDF
    with open(pdf_filename, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(pdf_filename))
    part["Content-Disposition"] = f'attachment; filename="{os.path.basename(pdf_filename)}"'
    msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, destinatario, msg.as_string())
        print(f"✅ Correo enviado correctamente a: {destinatario}")
        enviados += 1
    except Exception as e:
        print(f"❌ Error al enviar correo a {destinatario}: {e}")
        fallidos += 1

# === 📊 Resumen del proceso ===
print(f"\n📬 Resumen del envío:")
print(f"   ✅ Correos enviados correctamente: {enviados}")
print(f"   ❌ Fallos en el envío: {fallidos}")

if enviados == 0:
    exit(1)
else:
    print("🎯 Proceso de envío completado correctamente.")
