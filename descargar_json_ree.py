import requests
import json
import os
from datetime import datetime, timedelta

# Crear directorio de salida
os.makedirs("outputs", exist_ok=True)

# Fecha de hoy
fecha_hoy = datetime.now().strftime("%Y-%m-%d")

# Endpoint correcto de la API de ESIOS (PVPC)
url = (
    "https://api.esios.ree.es/indicators/1001?time_trunc=hour"
    f"&start_date={fecha_hoy}T00:00&end_date={fecha_hoy}T23:59"
)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Host": "api.esios.ree.es",
    "User-Agent": "Python Script",
}

print(f"🔍 Descargando datos PVPC para {fecha_hoy}...")

response = requests.get(url, headers=headers)

if response.status_code == 200:
    try:
        datos = response.json()
        json_file = f"outputs/pvpc-{fecha_hoy}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        print(f"✅ Datos guardados en {json_file}")
    except ValueError:
        print("❌ Error al decodificar JSON.")
else:
    print(f"❌ Error al descargar datos. Código: {response.status_code}")
    print(response.text[:500])
