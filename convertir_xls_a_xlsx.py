import pandas as pd
import os
from datetime import datetime

os.makedirs("downloads", exist_ok=True)

fecha_hoy = datetime.now()
# Ajustar fecha como en descargar para consistencia
if fecha_hoy.hour < 21:
    pass
else:
    fecha_hoy += timedelta(days=1)

fecha_archivo = fecha_hoy.strftime("%Y%m%d")

xls_path = f"downloads/pvpc_{fecha_archivo}.xls"
xlsx_path = f"downloads/pvpc_{fecha_archivo}.xlsx"

if not os.path.exists(xls_path):
    print(f"❌ No se encontró {xls_path}")
    exit(1)

try:
    print(f"🔄 Convirtiendo {xls_path} a {xlsx_path}")
    df = pd.read_excel(xls_path, engine='openpyxl' if xls_path.endswith('xlsx') else None)  # Auto-detecta
    df.to_excel(xlsx_path, index=False)
    print(f"✅ Conversión completa: {xlsx_path}")
except Exception as e:
    print(f"❌ Error al convertir: {str(e)}")
    exit(1)
