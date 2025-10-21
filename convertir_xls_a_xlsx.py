import pandas as pd
import os
from datetime import datetime

# Crear carpeta de salida
os.makedirs("downloads", exist_ok=True)

fecha_hoy = datetime.now().strftime("%Y-%m-%d")
xls_path = os.path.join("downloads", f"{fecha_hoy.replace('-', '')}-PVPC.xls")
xlsx_path = os.path.join("downloads", f"{fecha_hoy.replace('-', '')}-PVPC.xlsx")

if not os.path.exists(xls_path):
    print(f"❌ No se encontró el archivo {xls_path}")
    exit(1)

try:
    print(f"🔄 Convirtiendo {xls_path} a {xlsx_path}")
    df = pd.read_excel(xls_path, header=None)
    df.to_excel(xlsx_path, index=False)
    print(f"✅ Conversión completa: {xlsx_path}")
except Exception as e:
    print(f"❌ Error al convertir: {e}")
    exit(1)
