import requests
import json
import os
from datetime import datetime

# Crear directorio outputs si no existe
os.makedirs("outputs", exist_ok=True)

# Fecha actual
fecha_hoy = datetime.now().strftime("%Y-%m-%d")

# URL API REE PVPC
url = f"https://api.esios.ree.es/archives/71/download?date={fecha_hoy}"

headers = {"Accept": "application/json"}

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
        print("❌ Error: respuesta no JSON. Puede que el archivo sea distinto.")
else:
    print(f"❌ Error al descargar datos. Código: {response.status_code}")
