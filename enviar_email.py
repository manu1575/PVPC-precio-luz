import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime
import glob

EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
    print("❌ Faltan variables de entorno")
    exit(1)

print(f"📧 Configuración: Usuario {EMAIL_USER}, Destinatario {EMAIL_RECEIVER}")

pdf_files = sorted(glob.glob("outputs/pvpc_*.pdf"), key=os.path.getmtime, reverse=True)
if not pdf_files:
    print("❌ No PDFs en outputs/")
    exit(1)

pdf_file = pdf_files[0]
pdf_filename = os.path.basename(pdf_file)
pdf_size = os.path.getsize(pdf_file)
print(f"📎 PDF: {pdf_file} ({pdf_size/1024:.1f} KB)")

# Extraer fecha
try:
    fecha_str = pdf_filename.split('_')[1].split('.')[0]
    fecha = f"{fecha_str[0:4]}-{fecha_str[4:6]}-{fecha_str[6:8]}"
except:
    fecha = datetime.now().strftime('%Y-%m-%d')

msg = MIMEMultipart()
msg['From'] = EMAIL_USER
msg['To'] = EMAIL_RECEIVER
msg['Subject'] = f"⚡ Informe PVPC - {fecha}"

cuerpo = f"""
Hola,

Adjunto informe PVPC para {fecha}.

Incluye gráficos, estadísticas y tabla.

Datos de REE.

---
Automático via GitHub Actions. Envío: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

try:
    with open(pdf_file, "rb") as f:
        part = MIMEBase('application', 'pdf')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={pdf_filename}')
        msg.attach(part)
    print("✅ PDF adjuntado")
except Exception as e:
    print(f"❌ Error adjunto: {e}")
    exit(1)

print("📤 Enviando...")
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:  # Optimización: contexto
        server.set_debuglevel(1 if os.environ.get('DEBUG') else 0)  # Depuración condicional
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())
    print(f"✅ Enviado a {EMAIL_RECEIVER}")
except smtplib.SMTPAuthenticationError:
    print("❌ Autenticación fallida. Verifica credenciales/Gmail app password.")
    exit(1)
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)
