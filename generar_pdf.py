import json
import pandas as pd
import matplotlib.pyplot as plt
import pdfkit
import os
from datetime import datetime, timedelta

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

# Fecha para nombre
fecha_hoy = datetime.now()
if fecha_hoy.hour < 21:
    pass
else:
    fecha_hoy += timedelta(days=1)
fecha_archivo = fecha_hoy.strftime("%Y%m%d")

# Gráfico
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
ax.set_ylabel("Precio (€/kWh)")  # Claridad
ax.set_title("PVPC Diario")
ax.legend()

os.makedirs("outputs", exist_ok=True)
img_path = os.path.abspath("outputs/temp.png")
plt.savefig(img_path)
plt.close()

# HTML mejorado
html_content = """
<h1>PVPC Diario</h1>
<p>Estadísticas: Máximo: {:.4f} €/kWh, Mínimo: {:.4f} €/kWh, Medio: {:.4f} €/kWh</p>
{} 
<img src="{}" alt="Gráfico PVPC">
""".format(precios.max(), precios.min(), precios.mean(), df.to_html(index=False), img_path)

html_file = "outputs/temp.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

# Generar PDF
output_pdf = f"outputs/pvpc_{fecha_archivo}.pdf"
pdfkit.from_file(html_file, output_pdf)
print(f"✅ PDF generado: {output_pdf}")

# Limpieza opcional (optimización)
os.remove(html_file)
os.remove(img_path)

