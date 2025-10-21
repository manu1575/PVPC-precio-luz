import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime
import glob

# Variables de entorno
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

# Validar variables de entorno
if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
    print("❌ Faltan variables de entorno:")
    if not EMAIL_USER:
        print("   - EMAIL_USER")
    if not EMAIL_PASSWORD:
        print("   - EMAIL_PASSWORD")
    if not EMAIL_RECEIVER:
        print("   - EMAIL_RECEIVER")
    exit(1)

print(f"📧 Configuración de email:")
print(f"   Usuario: {EMAIL_USER}")
print(f"   Destinatario: {EMAIL_RECEIVER}")
print(f"   Servidor: {SMTP_SERVER}:{SMTP_PORT}")

# Buscar PDF más reciente
pdf_files = sorted(glob.glob("outputs/pvpc_*.pdf"), key=os.path.getmtime, reverse=True)

if not pdf_files:
    print("❌ No se encontraron PDFs generados en outputs/")
    print("💡 Ejecuta primero: python generar_pdf.py")
    exit(1)

pdf_file = pdf_files[0]
pdf_filename = os.path.basename(pdf_file)
pdf_size = os.path.getsize(pdf_file)

print(f"📎 PDF a enviar: {pdf_file}")
print(f"📦 Tamaño: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")

# Extraer fecha del nombre del archivo
try:
    fecha_str = pdf_filename.split('_')[1].split('.')[0]
    fecha = f"{fecha_str[0:4]}-{fecha_str[4:6]}-{fecha_str[6:8]}"
except:
    fecha = datetime.now().strftime('%Y-%m-%d')

# Crear mensaje
msg = MIMEMultipart()
msg['From'] = EMAIL_USER
msg['To'] = EMAIL_RECEIVER
msg['Subject'] = f"⚡ Informe PVPC diario - {fecha}"

# Cuerpo del mensaje
cuerpo = f"""
Hola,

Adjunto encontrarás el informe diario del Precio Voluntario para el Pequeño Consumidor (PVPC) correspondiente al día {fecha}.

El informe incluye:
• Gráficos de evolución horaria
• Estadísticas de precios (máximo, mínimo, medio)
• Tabla detallada por horas
• Clasificación por rangos de precio

Datos obtenidos de Red Eléctrica de España (REE).

---
Este es un mensaje automático generado por GitHub Actions.
Fecha de envío: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

# Adjuntar PDF
try:
    with open(pdf_file, "rb") as f:
        part = MIMEBase('application', 'pdf')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={pdf_filename}')
        msg.attach(part)
    
    print(f"✅ PDF adjuntado correctamente")

except Exception as e:
    print(f"❌ Error al adjuntar PDF: {e}")
    exit(1)

# Enviar email
print(f"📤 Enviando email...")

try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.set_debuglevel(0)  # Cambiar a 1 para debug
    
    print(f"🔐 Iniciando conexión TLS...")
    server.starttls()
    
    print(f"🔑 Autenticando...")
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    
    print(f"📨 Enviando mensaje...")
    server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())
    
    server.quit()
    
    print(f"✅ Email enviado exitosamente a {EMAIL_RECEIVER}")
    print(f"📄 Archivo adjunto: {pdf_filename} ({pdf_size/1024:.1f} KB)")

except smtplib.SMTPAuthenticationError:
    print("❌ Error de autenticación SMTP")
    print("💡 Verifica:")
    print("   - EMAIL_USER y EMAIL_PASSWORD son correctos")
    print("   - Si usas Gmail, necesitas una 'Contraseña de aplicación'")
    print("   - Accede a: https://myaccount.google.com/apppasswords")
    exit(1)

except smtplib.SMTPException as e:
    print(f"❌ Error SMTP: {e}")
    exit(1)

except Exception as e:
    print(f"❌ Error inesperado: {type(e).__name__}")
    print(f"📄 Detalle: {str(e)}")
    exit(1)
