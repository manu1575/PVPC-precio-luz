import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Evita errores en entornos sin display (como GitHub Actions)
import matplotlib.pyplot as plt
import pdfkit
import os
from datetime import datetime, timedelta

# === RUTAS Y ARCHIVO JSON ===
json_file = os.path.join("outputs", "pvpc.json")

if not os.path.exists(json_file):
    print("❌ No se encontró el archivo JSON de PVPC.")
    raise SystemExit(1)

# === CARGAR DATOS JSON ===
with open(json_file, "r", encoding="utf-8") as f:
    try:
        datos = json.load(f)
    except json.JSONDecodeError:
        print("❌ Error: El archivo JSON está corrupto o malformado.")
        raise SystemExit(1)

if "PVPC" not in datos:
    print("❌ Estructura JSON inválida: no contiene clave 'PVPC'.")
    raise SystemExit(1)

df = pd.DataFrame(datos["PVPC"])

# === FECHA DEL INFORME ===
fecha_hoy = datetime.now()
if fecha_hoy.hour >= 21:
    fecha_hoy += timedelta(days=1)

fecha_archivo = fecha_hoy.strftime("%Y%m%d")

# === GRÁFICO DE PRECIOS ===
fig, ax = plt.subplots(figsize=(10, 6))
precios = df["precio"]
horas = df["hora"]

# Umbrales de colores
umbral_bajo = precios.quantile(0.33)
umbral_alto = precios.quantile(0.66)

colores = []
for p in precios:
    if p <= umbral_bajo:
        colores.append("green")
    elif p <= umbral_alto:
        colores.append("orange")
    else:
        colores.append("red")

ax.bar(horas, precios, color=colores, edgecolor="black")
ax.axhline(precios.mean(), color="blue", linestyle="--", linewidth=1, label="Precio medio")

ax.set_xlabel("Hora del día", fontsize=10)
ax.set_ylabel("Precio (€/kWh)", fontsize=10)
ax.set_title(f"PVPC Diario - {fecha_hoy.strftime('%d/%m/%Y')}", fontsize=12, fontweight="bold")
ax.legend()

# Crear carpeta outputs si no existe
os.makedirs("outputs", exist_ok=True)

# Guardar gráfico temporal
img_path = os.path.abspath(os.path.join("outputs", "temp.png"))
plt.tight_layout()
plt.savefig(img_path, dpi=300)
plt.close(fig)

# === GENERAR HTML ===
html_content = f"""
<h1 style='font-family: Arial; text-align:center;'>Informe PVPC Diario</h1>
<p><b>Fecha:</b> {fecha_hoy.strftime('%d/%m/%Y')}</p>
<p><b>Máximo:</b> {precios.max():.4f} €/kWh &nbsp;&nbsp;
<b>Mínimo:</b> {precios.min():.4f} €/kWh &nbsp;&nbsp;
<b>Medio:</b> {precios.mean():.4f} €/kWh</p>
<br>
{df.to_html(index=False, border=0)}
<br><br>
<img src="{img_path}" alt="Gráfico PVPC" style="width:100%; max-width:700px;">
"""

html_file = os.path.join("outputs", "temp.html")
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

# === GENERAR PDF ===
output_pdf = os.path.join("outputs", f"pvpc_{fecha_archivo}.pdf")

try:
    pdfkit.from_file(html_file, output_pdf)
    print(f"✅ PDF generado correctamente: {output_pdf}")
except Exception as e:
    print(f"❌ Error al generar el PDF: {e}")

# === LIMPIEZA OPCIONAL ===
try:
    os.remove(html_file)
    os.remove(img_path)
except OSError:
    pass

