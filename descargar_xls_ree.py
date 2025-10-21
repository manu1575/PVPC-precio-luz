import requests
import os
from datetime import datetime

# Crear carpetas necesarias
os.makedirs("downloads", exist_ok=True)

# Fecha actual
fecha_hoy = datetime.now().strftime("%Y-%m-%d")

# URL pública del archivo XLS
url = f"https://api.esios.ree.es/archives/71/download?date={fecha_hoy}"

# Ruta de destino
xls_path = f"downloads/pvpc_{fecha_hoy}.xls"

print(f"🔽 Descargando archivo XLS de PVPC para {fecha_hoy}...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/octet-stream"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    with open(xls_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Archivo XLS descargado correctamente: {xls_path}")
else:
    print(f"❌ Error al descargar el archivo. Código: {response.status_code}")
    print(response.text)
