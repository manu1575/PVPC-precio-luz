# Descargará de forma automatizada el .xml diariamente del siguiente día, y a la hora programada. Si está vacio pesa 1Kb. 

import schedule
import time
import requests
import os
from datetime import datetime, timedelta

# Función que realiza la descarga
def descargar_archivo():
    # Calcular la fecha del día siguiente
    fecha_siguiente = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    fecha_formateada = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")  # Formato de la fecha como "YYYYMMDD"

    # Crear el nombre del archivo basado en la fecha
    nombre_archivo = f"{fecha_formateada}-PVPC.xls"

    # Definir la URL de la descarga utilizando la fecha calculada
    url = f"https://api.esios.ree.es/archives/71/download?date={fecha_siguiente}"

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

# Programar la tarea diaria a las 22:00 horas
schedule.every().day.at("22:36").do(descargar_archivo)

print("Tarea programada para las 22:00 horas cada día.")

# Mantener el programa ejecutándose
while True:
    schedule.run_pending()
    time.sleep(60)  # Esperar un minuto antes de verificar nuevamente
