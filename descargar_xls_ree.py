import requests
import os
from datetime import datetime, timedelta

# Crear carpetas necesarias
os.makedirs("downloads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Fecha actual (REE publica datos del día siguiente sobre las 20:15)
fecha_hoy = datetime.now()
# Si son antes de las 20:30, usar día anterior
if fecha_hoy.hour < 21:
    fecha_hoy = fecha_hoy - timedelta(days=1)

fecha_str = fecha_hoy.strftime("%Y-%m-%d")
fecha_archivo = fecha_hoy.strftime("%Y%m%d")

# URL pública del archivo XLS de PVPC
# API v1 de ESIOS - archivo 71 corresponde a PVPC
url = f"https://api.esios.ree.es/archives/71/download?date={fecha_str}"

# Ruta de destino (formato consistente)
xls_path = f"downloads/pvpc_{fecha_archivo}.xls"

print(f"📅 Fecha objetivo: {fecha_str}")
print(f"🔽 Descargando archivo XLS de PVPC desde REE...")
print(f"🌐 URL: {url}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/vnd.ms-excel, application/octet-stream, */*",
    "Accept-Language": "es-ES,es;q=0.9",
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        # Verificar que el contenido es un archivo Excel
        content_type = response.headers.get('Content-Type', '')
        if 'excel' in content_type.lower() or 'octet-stream' in content_type.lower():
            with open(xls_path, "wb") as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ Archivo descargado correctamente: {xls_path}")
            print(f"📊 Tamaño: {file_size:,} bytes")
            
            # Guardar metadata
            with open(f"downloads/metadata_{fecha_archivo}.txt", "w") as f:
                f.write(f"Fecha: {fecha_str}\n")
                f.write(f"Descarga: {datetime.now().isoformat()}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Tamaño: {file_size} bytes\n")
        else:
            print(f"⚠️  Tipo de contenido inesperado: {content_type}")
            print(f"❌ El servidor no devolvió un archivo Excel válido")
            # Guardar respuesta para debug
            with open("downloads/error_response.txt", "w") as f:
                f.write(f"Status: {response.status_code}\n")
                f.write(f"Headers: {response.headers}\n")
                f.write(f"Content: {response.text[:1000]}\n")
            exit(1)
    else:
        print(f"❌ Error al descargar el archivo")
        print(f"📛 Código HTTP: {response.status_code}")
        print(f"📄 Respuesta: {response.text[:500]}")
        
        # Guardar error para análisis
        with open("downloads/error_log.txt", "w") as f:
            f.write(f"Fecha intento: {datetime.now().isoformat()}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Status: {response.status_code}\n")
            f.write(f"Response: {response.text}\n")
        
        exit(1)

except requests.exceptions.Timeout:
    print("❌ Timeout: El servidor tardó demasiado en responder")
    exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Error de conexión: No se pudo conectar con el servidor")
    exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {type(e).__name__}")
    print(f"📄 Detalle: {str(e)}")
    exit(1)
