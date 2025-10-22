import requests
import os
import json
from datetime import datetime, timedelta
import pandas as pd  # Para extracción de hora (opcional, pero optimiza)

# Token desde variable de entorno (secrets en GitHub Actions)
TOKEN = os.environ.get('ESIOS_TOKEN')
if not TOKEN:
    raise ValueError("❌ ESIOS_TOKEN no configurado en secrets de GitHub o entorno local. Verifique configuración.")

os.makedirs("outputs", exist_ok=True)

# Lógica de fecha: Día siguiente si después de las 20:15
now = datetime.now()
publication_time = now.replace(hour=20, minute=15, second=0, microsecond=0)
if now >= publication_time:
    target_date = now + timedelta(days=1)
else:
    target_date = now
start_date = target_date.strftime("%Y-%m-%dT00:00")
end_date = target_date.strftime("%Y-%m-%dT23:59")

# Condicional de salida temprana: Si PDF ya existe, salir
fecha_archivo = target_date.strftime("%Y%m%d")
pdf_path = f"outputs/pvpc_{fecha_archivo}.pdf"
if os.path.exists(pdf_path):
    print(f"✅ PDF para {fecha_archivo} ya generado en ejecución anterior. Saliendo.")
    exit(0)

# Endpoint para PVPC (indicator 1001)
url = "https://api.esios.ree.es/indicators/1001"
params = {
    "start_date": start_date,
    "end_date": end_date,
    "time_trunc": "hour"
}
headers = {
    "Accept": "application/json; application/vnd.esios-api-v2+json",
    "Content-Type": "application/json",
    "x-api-key": TOKEN
}

print(f"📅 Descargando datos PVPC para {target_date.strftime('%Y-%m-%d')}...")

try:
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    # Validar estructura
    if 'indicator' not in data or 'values' not in data['indicator']:
        raise ValueError("❌ Estructura JSON inesperada")

    # Verificación de fecha: Asegurar datos para target_date
    expected_date = target_date.strftime("%Y-%m-%d")
    dates_in_data = [datetime.fromisoformat(item['datetime'].replace('Z', '+00:00')).strftime("%Y-%m-%d") for item in data['indicator']['values']]
    if expected_date not in set(dates_in_data):
        print(f"⚠️ Datos no incluyen {expected_date}. Ejecuciones subsiguientes continuarán.")
        exit(0)  # Salir sin procesar, pero sin error fatal

    # Filtrar y procesar (geo_id=8741 para Península)
    pvpc_list = []
    for item in data['indicator']['values']:
        if item.get('geo_id') == 8741:
            dt = datetime.fromisoformat(item['datetime'].replace('Z', '+00:00'))
            hora = dt.strftime("%H-%M")  # Ajustable a "00-01" si necesario
            precio = item['value'] / 1000  # €/MWh a €/kWh
            pvpc_list.append({"hora": hora, "precio": precio})

    if not pvpc_list:
        raise ValueError("❌ No se encontraron datos para Península")

    output_data = {"PVPC": pvpc_list}
    json_path = "outputs/pvpc.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"✅ JSON procesado y guardado en {json_path} ({len(pvpc_list)} horas)")

except requests.exceptions.RequestException as e:
    print(f"❌ Error en descarga: {str(e)} - Código: {response.status_code if 'response' in locals() else 'N/A'}")
    exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {str(e)}")
    exit(1)
