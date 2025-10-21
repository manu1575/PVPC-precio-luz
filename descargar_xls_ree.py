import requests
import os
from datetime import datetime

# Crear carpetas si no existen
os.makedirs("downloads", exist_ok=True)

# Fecha de hoy
fecha_hoy = datetime.now().strftime("%Y-%m-%d")

# URL pública de descarga del archivo XLS de REE (PVPC)
url = f"https://api.esios.ree.es/archives/71/download?date={fecha_hoy}"

# Nombre de salida
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
    print(f"✅ Archivo descargado correctamente: {xls_path}")
else:
    print(f"❌ Error al descargar. Código: {response.status_code}")
    print(response.text)
