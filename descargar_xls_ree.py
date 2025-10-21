import requests
import os
from datetime import datetime

# Crear carpetas si no existen
os.makedirs("downloads", exist_ok=True)

# Fecha actual
fecha_hoy = datetime.now().strftime("%Y-%m-%d")

# URL de descarga del XLS público de REE
url = f"https://api.esios.ree.es/archives/71/download?date={fecha_hoy}"

# Nombre del archivo XLS
xls_filename = f"{fecha_hoy.replace('-', '')}-PVPC.xls"
xls_path = os.path.join("downloads", xls_filename)

print(f"🔍 Descargando XLS desde {url}")

response = requests.get(url)
if response.status_code == 200:
    with open(xls_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Archivo guardado: {xls_path}")
else:
    print(f"❌ Error al descargar archivo. Código {response.status_code}")
    exit(1)

