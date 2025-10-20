import pandas as pd
import pdfkit
import os

# Archivo procesado
processed_file = "downloads/processed_data.xlsx"
if not os.path.exists(processed_file):
    print("Archivo procesado no encontrado.")
    exit(1)

# Leer datos
df = pd.read_excel(processed_file)

# Convertir a HTML temporal
html_file = "downloads/temp.html"
df.to_html(html_file, index=False)

# Generar PDF final
output_pdf = "output.pdf"
pdfkit.from_file(html_file, output_pdf)

print(f"PDF generado en: {output_pdf}")
