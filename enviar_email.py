import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Leer secretos del entorno
EMAIL_USER = os.environ[jmtijada@hotmail.com]
EMAIL_PASSWORD = os.environ[BtPbnKenARA9pVS]
EMAIL_RECEIVER = os.environ[renderiza@gmx.com]
SMTP_SERVER = os.environ[mail.gmx.com]
SMTP_PORT = int(os.environ[465])

# Configurar correo
msg = MIMEMultipart()
msg['From'] = EMAIL_USER
msg['To'] = EMAIL_RECEIVER
msg['Subject'] = "Archivo PDF diario PVPC"

body = "Adjunto el archivo PDF generado automáticamente."
msg.attach(MIMEText(body, 'plain'))

# Adjuntar PDF
filename = f"outputs/output-{os.popen('date +%Y%m%d').read().strip()}.pdf"
with open(filename, "rb") as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={filename}')
    msg.attach(part)

# Enviar correo
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(EMAIL_USER, EMAIL_PASSWORD)
server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())
server.quit()

print(f"Email enviado a {EMAIL_RECEIVER} con el archivo {filename}")
