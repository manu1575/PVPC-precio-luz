import json
import pandas as pd
import matplotlib.pyplot as plt
import pdfkit
import os
from datetime import datetime, timedelta

# === Cargar JSON de PVPC ===
json_file = "outputs/pvpc.json"
if not os.path.exists(json_file):
    print("❌ No hay JSON de PVPC")
    exit(1)

with open(json_file, "r", encoding="utf-8") as f:
    datos = json.load(f)

try:
    df = pd.DataFrame(datos["PVPC"])
except KeyError:
    print("❌ Estructura JSON inválida")
    exit(1)

# === Preparar fecha para nombre del archivo ===
fecha_hoy = datetime.now()
if fecha_hoy.hour >= 21:
    fecha_hoy += timedelta(days=1)
fecha_archivo = fecha_hoy.strftime("%Y%m%d")

# === Crear gráfico ===
fig, ax = plt.subplots(figsize=(10, 6))
precios = df["precio"]
horas = df["hora"]

colores = []
umbral_bajo = precios.quantile(0.33)
umbral_alto = precios.quantile(0.66)
for p in precios:
    if p <= umbral_bajo:
        colores.append("green")
    elif p <= umbral_alto:
        colores.append("yellow")
    else:
        colores.append("red")

ax.bar(horas, precios, color=colores)
ax.axhline(precios.mean(), color="blue", linestyle="--", label="Precio medio")
ax.set_xlabel("Hora")
ax.set_ylabel("Precio (€/kWh)")
ax.set_title("PVPC Diario")
ax.legend()

os.makedirs("outputs", exist_ok=True)
img_path = os.path.abspath("outputs/temp.png")
plt.savefig(img_path)
plt.close()

# === Crear HTML temporal con gráfico ===
# Usar ruta absoluta file:// para evitar errores de acceso en wkhtmltopdf
img_path_uri = f"file://{img_path}"

html_content = f"""
<h1>PVPC Diario</h1>
<p>Estadísticas:</p>
<ul>
  <li>Máximo: {precios.max():.4f} €/kWh</li>
  <li>Mínimo: {precios.min():.4f} €/kWh</li>
  <li>Medio: {precios.mean():.4f} €/kWh</li>
</ul>
{df.to_html(index=False)} 
<br>
<img src="{img_path_uri}" alt="Gráfico PVPC" style="width:90%;margin-top:20px;">
"""

html_file = "outputs/temp.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

# === Generar PDF con configuración local ===
output_pdf = f"outputs/pvpc_{fecha_archivo}.pdf"

# Configurar wkhtmltopdf para GitHub Actions
config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")

options = {
    "enable-local-file-access": None,  # Permitir acceso a archivos locales
    "quiet": "",                       # Suprimir mensajes
    "encoding": "UTF-8",
    "page-size": "A4",
    "margin-top": "10mm",
    "margin-right": "10mm",
    "margin-bottom": "10mm",
    "margin-left": "10mm",
}

pdfkit.from_file(html_file, output_pdf, configuration=config, options=options)
print(f"✅ PDF generado correctamente: {output_pdf}")

# === Limpieza de archivos temporales ===
try:
    os.remove(html_file)
    os.remove(img_path)
except Exception as e:
    print(f"⚠️ Limpieza incompleta: {e}")
