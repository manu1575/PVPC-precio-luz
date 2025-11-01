import json
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
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

# === Fecha para nombre ===
fecha_hoy = datetime.now()
if fecha_hoy.hour >= 21:
    fecha_hoy += timedelta(days=1)
fecha_archivo = fecha_hoy.strftime("%Y%m%d")

# === Crear gráfico ===
fig, ax = plt.subplots(figsize=(12, 6))
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

bars = ax.bar(horas, precios, color=colores)
ax.axhline(precios.mean(), color="blue", linestyle="--", label="Precio medio")
ax.set_xlabel("Hora")
ax.set_ylabel("Precio (€/kWh)")
ax.set_title("PVPC Diario")
ax.legend()
plt.xticks(rotation=45, ha='right')  # evita solapamiento de horas
plt.tight_layout()

os.makedirs("outputs", exist_ok=True)
img_path = os.path.abspath("outputs/temp.png")
plt.savefig(img_path, bbox_inches="tight")
plt.close()

# === Crear PDF con ReportLab en horizontal ===
output_pdf = f"outputs/pvpc_{fecha_archivo}.pdf"
c = canvas.Canvas(output_pdf, pagesize=landscape(A4))
width, height = landscape(A4)

# Título
c.setFont("Helvetica-Bold", 18)
c.drawString(50, height - 50, "Informe Diario PVPC")

# Estadísticas
c.setFont("Helvetica", 12)
texto = f"""
Fecha: {fecha_hoy.strftime('%d/%m/%Y')}
Precio máximo: {precios.max():.4f} €/kWh
Precio mínimo: {precios.min():.4f} €/kWh
Precio medio:  {precios.mean():.4f} €/kWh
"""
for i, linea in enumerate(texto.strip().split("\n")):
    c.drawString(50, height - 90 - (i * 15), linea)

# Insertar gráfico
img = ImageReader(img_path)
c.drawImage(img, 50, height / 2 - 70, width=width - 100, preserveAspectRatio=True, mask="auto")

# Tabla de precios más cercana al gráfico, con colores
c.setFont("Helvetica-Bold", 12)
c.drawString(50, height / 2 - 150, "Tabla de precios por hora:")

c.setFont("Helvetica", 10)
y = height / 2 - 170
for i, row in df.iterrows():
    line = f"{row['hora']}: {row['precio']:.4f} €/kWh"
    # Colorear según precio
    if row['precio'] <= umbral_bajo:
        c.setFillColor(colors.green)
    elif row['precio'] <= umbral_alto:
        c.setFillColor(colors.yellow)
    else:
        c.setFillColor(colors.red)
    c.drawString(60, y, line)
    y -= 12

c.setFillColor(colors.black)  # reset color

c.save()
print(f"✅ PDF generado correctamente: {output_pdf}")

# === Limpieza ===
try:
    os.remove(img_path)
except Exception as e:
    print(f"⚠️ Limpieza incompleta: {e}")
