import os
import glob
import pandas as pd

# Buscar el archivo .xls más reciente en downloads/
xls_files = glob.glob("downloads/*.xls")
if not xls_files:
    print("No se encontró ningún archivo .xls en downloads/")
    exit(1)

xls_file = max(xls_files, key=os.path.getctime)
xlsx_file = xls_file.replace(".xls", ".xlsx")

# Leer .xls y guardar como .xlsx
df = pd.read_excel(xls_file, engine='xlrd')
df.to_excel(xlsx_file, index=False)
print(f"Archivo convertido: {xls_file} → {xlsx_file}")
