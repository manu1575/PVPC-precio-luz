 #Descargar el .xml sin programación

import requests
import os
from datetime import datetime

# Definir la URL de la descarga
url = "https://api.esios.ree.es/archives/71/download?date=2025-01-05"

# Extraer la fecha de la URL
fecha_url = url.split("date=")[-1]  # Obtener la fecha después de "date="
fecha_formateada = datetime.strptime(fecha_url, "%Y-%m-%d").strftime("%Y%m%d")  # Formatear la fecha como "YYYYMMDD"

# Crear el nombre del archivo
nombre_archivo = f"{fecha_formateada}-PVPC.xls"

# Ruta de la carpeta "Descargas" (en Windows)
descargas_path = os.path.join(os.path.expanduser('~'), 'Downloads')

# Asegurarnos de que el directorio de "Descargas" exista
os.makedirs(descargas_path, exist_ok=True)

# Ruta completa del archivo donde se guardará
ruta_completa = os.path.join(descargas_path, nombre_archivo)

# Hacer la solicitud GET para descargar el archivo
print(f"Iniciando descarga desde la URL: {url}")
response = requests.get(url)

# Verificar si la solicitud fue exitosa (Código 200)
if response.status_code == 200:
    # Guardar el contenido del archivo en la ruta especificada
    with open(ruta_completa, 'wb') as f:
        f.write(response.content)
    print(f"Archivo descargado y guardado en: {ruta_completa}")
else:
    print(f"Error al descargar el archivo. Código de estado: {response.status_code}")
