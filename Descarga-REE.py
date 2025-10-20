import requests
import os
from datetime import datetime, timedelta

# Calcular la fecha del día siguiente (o la fecha que necesites)
fecha_siguiente = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
fecha_formateada = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")  # YYYYMMDD

# Crear el nombre del archivo
nombre_archivo = f"{fecha_formateada}-PVPC.xls"

# Carpeta para guardar descargas dentro del repositorio/runner
descargas_path = os.path.join(os.getcwd(), "downloads")
os.makedirs(descargas_path, exist_ok=True)

# Ruta completa del archivo donde se guardará
ruta_completa = os.path.join(descargas_path, nombre_archivo)

# Definir la URL de descarga usando la fecha calculada
url = f"https://api.esios.ree.es/archives/71/download?date={fecha_siguiente}"

# Hacer la solicitud GET para descargar el archivo
print(f"Iniciando descarga desde la URL: {url}")
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    with open(ruta_completa, 'wb') as f:
        f.write(response.content)
    print(f"Archivo descargado y guardado en: {ruta_completa}")
else:
    print(f"Error al descargar el archivo. Código de estado: {response.status_code}")
