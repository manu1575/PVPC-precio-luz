import requests
import os
import json
from datetime import datetime, timedelta

# Token desde variable de entorno
TOKEN = os.environ.get('ESIOS_TOKEN')
if not TOKEN:
    raise ValueError("❌ ESIOS_TOKEN no configurado en secrets o entorno local.")

os.makedirs("outputs", exist_ok=True)

# Lógica de fecha: día siguiente si después de las 20:15
now = datetime.now()
publication_time = now.replace(hour=20, minute=15, second=0, microsecond=0)
target_date = now + timedelta(days=1) if now >= publication_time else now
start_date = target_date.strftime("%Y-%m-%dT00:00")
end_date = target_date.strftime("%Y-%m-%dT23:59")

# JSON de salida
json_path = "outputs/pvpc.json"

# Endpoint PVPC
url = "https://api.esios.ree.es/indicators/1001"
params = {"start_date": start_date, "end_date": end_date, "time_trunc": "hour"}
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

    if 'indicator' not in data or 'values' not in data['indicator']:
        raise ValueError("❌ Estructura JSON inesperada")

    # Filtrar datos Península (geo_id=8741)
    pvpc_list = []
    for item in data['indicator']['values']:
        if item.get('geo_id') == 8741:
            dt = datetime.fromisoformat(item['datetime'].replace('Z', '+00:00'))
            hora = dt.strftime("%H-%M")
            precio = item['value'] / 1000  # €/MWh → €/kWh
            pvpc_list.append({"hora": hora, "precio": precio})

    if not pvpc_list:
        raise ValueError("❌ No se encontraron datos para Península")

    # Guardar JSON siempre
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"PVPC": pvpc_list}, f, ensure_ascii=False, indent=4)

    print(f"✅ JSON procesado y guardado en {json_path} ({len(pvpc_list)} horas)")

except requests.exceptions.RequestException as e:
    print(f"❌ Error en descarga: {str(e)}")
    exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {str(e)}")
    exit(1)
