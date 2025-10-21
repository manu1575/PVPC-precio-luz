import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

EMAIL_USER = os.environ['EMAIL_USER']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
EMAIL_RECEIVER = os.environ['EMAIL_RECEIVER']
SMTP_SERVER = os.environ['SMTP_SERVER']
SMTP_PORT = int(os.environ['SMTP_PORT'])

# Buscar PDF más reciente
pdf_files = sorted([f for f in os.listdir("outputs") if f.endswith(".pdf")])
if not pdf_files:
    print("❌ No hay PDFs generados")
    exit(1)
pdf_file = os.path.join("outputs", pdf_files[-1])

# Crear mensaje
msg = MIMEMultipart()
msg['From'] = EMAIL_USER
msg['To'] = EMAIL_RECEIVER
msg['Subject'] = f"Informe PVPC diario - {datetime.now().strftime('%Y-%m-%d')}"
msg.attach(MIMEText("Adjunto el PDF con los precios PVPC diario.", 'plain'))

# Adjuntar PDF
with open(pdf_file, "rb") as f:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={pdf_file}')
    msg.attach(part)

# Enviar email
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(EMAIL_USER, EMAIL_PASSWORD)
server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())
server.quit()

print(f"✅ Email enviado a {EMAIL_RECEIVER} con {pdf_file}")
