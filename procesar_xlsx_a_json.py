import pandas as pd
import os
import json
from datetime import datetime, timedelta

fecha_hoy = datetime.now()
if fecha_hoy.hour < 21:
    pass
else:
    fecha_hoy += timedelta(days=1)

fecha_archivo = fecha_hoy.strftime("%Y%m%d")
xlsx_path = f"downloads/pvpc_{fecha_archivo}.xlsx"
json_path = "outputs/pvpc.json"

if not os.path.exists(xlsx_path):
    print(f"❌ No se encontró {xlsx_path}")
    exit(1)

try:
    # Leer XLSX (asumiendo estructura estándar: headers en fila 1, columnas 'Hora', 'PCB' para precio general)
    df = pd.read_excel(xlsx_path, skiprows=0)  # Ajustar skiprows si hay cabeceras extras (depurar con print(df.head()))
    
    # Depuración: Mostrar columnas disponibles
    print(f"📊 Columnas detectadas: {df.columns.tolist()}")
    
    # Procesar precio (PCB: €/MWh con ',' -> float €/kWh)
    if 'PCB' not in df.columns or 'Hora' not in df.columns:
        raise ValueError("Estructura XLS inesperada: faltan columnas 'Hora' o 'PCB'")
    
    df['precio'] = df['PCB'].astype(str).str.replace(',', '.').astype(float) / 1000  # Optimización: vectorizado
    df['hora'] = df['Hora']
    
    # Datos para JSON
    datos = {"PVPC": df[['hora', 'precio']].to_dict(orient='records')}
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
    
    print(f"✅ JSON generado: {json_path}")
except Exception as e:
    print(f"❌ Error al procesar XLSX: {str(e)}")
    exit(1)
