import requests
import os
from datetime import datetime, timedelta

os.makedirs("downloads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

fecha_hoy = datetime.now()
if fecha_hoy.hour >= 21:
    fecha_hoy += timedelta(days=1)  # Después de las 21:00, usar día siguiente (precios recién publicados)
# Antes de las 21:00, usar día actual (precios del día, publicados ayer)

fecha_str = fecha_hoy.strftime("%Y-%m-%d")
fecha_archivo = fecha_hoy.strftime("%Y%m%d")

url = f"https://api.esios.ree.es/archives/71/download?date={fecha_str}"
xls_path = f"downloads/pvpc_{fecha_archivo}.xls"

print(f"📅 Fecha objetivo (más reciente disponible): {fecha_str}")
print(f"🔽 Descargando XLS de PVPC desde REE...")
print(f"🌐 URL: {url}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/vnd.ms-excel, application/octet-stream, */*",
    "Accept-Language": "es-ES,es;q=0.9",
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()  # Optimización: raise error si no 200
    
    content_type = response.headers.get('Content-Type', '')
    if 'excel' in content_type.lower() or 'octet-stream' in content_type.lower():
        with open(xls_path, "wb") as f:
            f.write(response.content)
        file_size = os.path.getsize(xls_path)
        print(f"✅ Archivo descargado: {xls_path} ({file_size:,} bytes)")
        
        # Metadata para depuración
        with open(f"downloads/metadata_{fecha_archivo}.txt", "w") as f:
            f.write(f"Fecha: {fecha_str}\nDescarga: {datetime.now().isoformat()}\nURL: {url}\nTamaño: {file_size} bytes\n")
    else:
        raise ValueError(f"Tipo de contenido inesperado: {content_type}")
except requests.exceptions.RequestException as e:
    print(f"❌ Error en descarga: {str(e)}")
    with open("downloads/error_log.txt", "w") as f:
        f.write(f"Intento: {datetime.now().isoformat()}\nURL: {url}\nError: {str(e)}\n")
    exit(1)
