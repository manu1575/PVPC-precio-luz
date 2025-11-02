import json
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os
from datetime import datetime

# === Cargar JSON ===
json_file = "outputs/pvpc.json"
if not os.path.exists(json_file):
    print("❌ No hay JSON de PVPC")
    exit(1)

with open(json_file, "r", encoding="utf-8") as f:
    datos = json.load(f)

df = pd.DataFrame(datos["PVPC"])

# === Tomar la fecha de publicación del JSON ===
fecha_json = datos.get("fecha_publicacion")
if not fecha_json:
    print("⚠️ No se encontró 'fecha_publicacion' en el JSON. Se usará la fecha actual.")
    fecha_json = datetime.now().strftime("%Y-%m-%d")

fecha_dt = datetime.strptime(fecha_json, "%Y-%m-%d")
fecha_archivo = fecha_dt.strftime("%Y%m%d")
output_pdf = f"outputs/pvpc_{fecha_archivo}.pdf"

# === Crear gráfico ligeramente más pequeño ===
fig, ax = plt.subplots(figsize=(10, 5))
precios = df["precio"]
horas = df["hora"]

umbral_bajo = precios.quantile(0.33)
umbral_alto = precios.quantile(0.66)

# Colores para el gráfico y la tabla: verde, dorado fuerte, rojo
colores_barras = [
    'green' if p <= umbral_bajo else '#E1A500' if p <= umbral_alto else 'red'
    for p in precios
]

ax.bar([h.replace("-", ",") for h in horas], precios, color=colores_barras)
ax.axhline(precios.mean(), color="blue", linestyle="--",
            label=f"Precio medio: {precios.mean():.4f} €/kWh")
ax.set_xlabel("Hora")
ax.set_ylabel("Precio (€/kWh)")
ax.set_title(f"PVPC Diario {fecha_dt.strftime('%d/%m/%Y')}")
ax.legend()
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

os.makedirs("outputs", exist_ok=True)
img_path = os.path.abspath("outputs/temp.png")
plt.savefig(img_path, bbox_inches="tight")
plt.close()

# === Crear PDF vertical A4 ===
c = canvas.Canvas(output_pdf, pagesize=A4)
width, height = A4

# Título
c.setFont("Helvetica-Bold", 18)
c.drawString(50, height - 50, f"Informe Diario PVPC – {fecha_dt.strftime('%d/%m/%Y')}")

# Estadísticas
c.setFont("Helvetica", 12)
texto = f"""
Precio máximo: {precios.max():.4f} €/kWh
Precio mínimo: {precios.min():.4f} €/kWh
Precio medio:  {precios.mean():.4f} €/kWh
"""
for i, linea in enumerate(texto.strip().split("\n")):
    c.drawString(50, height - 90 - (i * 15), linea)

# Insertar gráfico
img = ImageReader(img_path)
c.drawImage(img, 50, height / 2 - 40, width=width - 100,
            preserveAspectRatio=True, mask="auto")

# Tabla de precios justo debajo del gráfico (distancia reducida)
c.setFont("Helvetica-Bold", 12)
c.drawString(50, height / 2 - 10, "Tabla de precios por hora:")

c.setFont("Helvetica", 10)
y = height / 2 - 30
for _, row in df.iterrows():
    line = f"{row['hora'].replace('-', ',')}: {row['precio']:.4f} €/kWh"
    if row['precio'] <= umbral_bajo:
        c.setFillColor(colors.green)
    elif row['precio'] <= umbral_alto:
        c.setFillColor(colors.Color(0.85, 0.65, 0.0))  # dorado más oscuro
    else:
        c.setFillColor(colors.red)
    c.drawString(60, y, line)
    y -= 12

c.setFillColor(colors.black)
c.save()

# Limpieza
try:
    os.remove(img_path)
except Exception as e:
    print(f"⚠️ Limpieza incompleta: {e}")

print(f"✅ PDF generado correctamente: {output_pdf}")
