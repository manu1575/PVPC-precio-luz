import requests
import os
import json
from datetime import datetime, timedelta
import pandas as pd  # Para extracción de hora

# Token como variable de entorno
TOKEN = os.environ.get('ESIOS_TOKEN')
if not TOKEN:
    raise ValueError("❌ ESIOS_TOKEN no configurado. Solicite uno a consultasios@ree.es")

os.makedirs("outputs", exist_ok=True)

# Lógica de fecha: Día siguiente si después de las 20:15, pero ajustado para intentos
now = datetime.now()
publication_time = now.replace(hour=20, minute=15, second=0, microsecond=0)
target_date = now + timedelta(days=1) if now >= publication_time else now

# Condicional de salida temprana: Chequear si PDF ya existe
fecha_archivo = target_date.strftime("%Y%m%d")
pdf_path = f"outputs/pvpc_{fecha_archivo}.pdf"
if os.path.exists(pdf_path):
    print(f"✅ PDF para {fecha_archivo} ya generado. Saliendo sin procesar.")
    exit(0)

# ... (resto del código: params, headers, requests.get, validación de estructura)

# Verificación de fecha post-descarga
expected_date = target_date.strftime("%Y-%m-%d")
dates_in_data = [datetime.fromisoformat(item['datetime'].replace('Z', '+00:00')).strftime("%Y-%m-%d") for item in data['indicator']['values']]
if expected_date not in set(dates_in_data):
    print(f"⚠️ Datos no incluyen {expected_date}. Intentos subsiguientes continuarán.")
    exit(0)  # Salir sin error para no fallar el workflow

# ... (procesamiento de pvpc_list y guardado de JSON)
