import requests
import os
import json
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import pytz  # Para huso horario Madrid

# === Variables de entorno ===
TOKEN = os.environ.get('ESIOS_TOKEN')
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', '')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

if not TOKEN:
    raise ValueError("❌ Falta ESIOS_TOKEN en secretos del repositorio.")

os.makedirs("outputs", exist_ok=True)

# === Función para enviar correo de alerta ===
def enviar_alerta(asunto, cuerpo):
    if not EMAIL_USER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
        print("⚠️ Notificación desactivada: faltan credenciales de correo.")
        return
    destinatarios = [x.strip() for x in EMAIL_RECEIVER.split(",") if x.strip()]
    msg = MIMEText(cuerpo)
    msg["Subject"] = asunto
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(destinatarios)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, destinatarios, msg.as_string())
        print(f"📧 Notificación enviada a: {msg['To']}")
    except Exception as e:
        print(f"⚠️ No se pudo enviar la notificación: {e}")

# === Configuración de fechas ===
zona_madrid = pytz.timezone("Europe/Madrid")
ahora = datetime.now(zona_madrid)
# Día siguiente si ya son las 21:40 o más
target_date = ahora.date()
if ahora.hour > 21 or (ahora.hour == 21 and ahora.minute >= 40):
    target_date += timedelta(days=1)

start_date = f"{target_date}T00:00"
end_date = f"{target_date}T23:59"

# === Archivos ===
fecha_archivo = target_date.strftime("%Y%m%d")
pdf_path = f"outputs/pvpc_{fecha_archivo}.pdf"
json_path = "outputs/pvpc.json"

# === Evitar reejecución innecesaria ===
if os.path.exists(pdf_path):
    print(f"✅ PDF para {fecha_archivo} ya generado en ejecución anterior. Saliendo.")
    exit(0)

# === Pausa inicial para asegurar entorno listo ===
print("⏳ Esperando 30 segundos antes de iniciar la descarga...")
time.sleep(30)

# === Descarga con reintentos ===
url = "https://api.esios.ree.es/indicators/1001"
headers = {
    "Accept": "application/json; application/vnd.esios-api-v2+json",
    "Content-Type": "application/json",
    "x-api-key": TOKEN
}
params = {
    "start_date": start_date,
    "end_date": end_date,
    "time_trunc": "hour"
}

MAX_INTENTOS = 5
ESPERA_SEGUNDOS = 20 * 60  # 20 minutos
exito = False

for intento in range(1, MAX_INTENTOS + 1):
    print(f"🔄 Intento {intento}/{MAX_INTENTOS} para descargar datos de {target_date}")
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        valores = data.get("indicator", {}).get("values", [])
        if not valores:
            raise ValueError("Datos vacíos o incompletos")

        # Confirmar que los datos son del target_date
        fechas = [datetime.fromisoformat(v["datetime"].replace("Z", "+00:00")).astimezone(zona_madrid).date()
                  for v in valores]
        if target_date not in fechas:
            print(f"⚠️ Datos aún no actualizados ({intento}/{MAX_INTENTOS})")
            if intento < MAX_INTENTOS:
                time.sleep(ESPERA_SEGUNDOS)
            continue

        # Procesar datos PVPC Península
        pvpc = []
        for v in valores:
            if v.get("geo_id") == 8741:
                dt = datetime.fromisoformat(v["datetime"].replace("Z", "+00:00")).astimezone(zona_madrid)
                hora = dt.strftime("%H,%M")
                precio = v["value"] / 1000
                pvpc.append({"hora": hora, "precio": precio})

        if not pvpc:
            raise ValueError("No se encontraron datos Península")

        salida = {
            "fecha_publicacion": str(target_date),
            "PVPC": pvpc
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(salida, f, ensure_ascii=False, indent=4)

        # Validar tamaño del archivo
        if os.path.exists(json_path) and os.path.getsize(json_path) > 500:
            print(f"✅ JSON generado correctamente: {json_path} ({os.path.getsize(json_path)} bytes)")
        else:
            raise ValueError("⚠️ El archivo JSON se creó pero parece estar vacío o incompleto.")

        exito = True
        break

    except Exception as e:
        print(f"❌ Error en intento {intento}: {e}")
        if intento < MAX_INTENTOS:
            time.sleep(ESPERA_SEGUNDOS)

# === Verificación final antes de terminar ===
if not exito or not os.path.exists(json_path):
    mensaje = (
        f"No se han podido obtener los datos PVPC del día {target_date.strftime('%d/%m/%Y')} "
        f"tras {MAX_INTENTOS} intentos. Es posible que REE no haya publicado aún la información."
    )
    enviar_alerta("⚠️ Error en descarga de datos PVPC", mensaje)
    print("❌ Proceso detenido: no se generó el JSON esperado.")
    exit(1)

import hashlib

print("Huella SHA-256 del token de GitHub:",
      hashlib.sha256(TOKEN.encode()).hexdigest())
# Espera adicional para asegurar sincronización de escritura en disco
time.sleep(5)
print("🕒 Espera final de sincronización completada. JSON disponible y verificado.")
