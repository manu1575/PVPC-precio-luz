import os
import glob
import pandas as pd

# Buscar el archivo .xlsx más reciente en downloads/
xlsx_files = glob.glob("downloads/*.xlsx")
if not xlsx_files:
    print("No se encontró ningún archivo .xlsx en downloads/")
    exit(1)

xlsx_file = max(xlsx_files, key=os.path.getctime)
processed_file = "downloads/processed_data.xlsx"

# Leer el .xlsx
df = pd.read_excel(xlsx_file)

# Ejemplo de procesamiento: filtrar solo columnas necesarias
# Ajusta según tus necesidades
columns_to_keep = df.columns[:5]  # solo las primeras 5 columnas de ejemplo
df_processed = df[columns_to_keep]

# Guardar el archivo procesado
df_processed.to_excel(processed_file, index=False)
print(f"Datos procesados guardados en: {processed_file}")
