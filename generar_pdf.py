import json
import pandas as pd
import matplotlib.pyplot as plt
import pdfkit
import os
import base64
from io import BytesIO
from datetime import datetime, timedelta

# === 1. Cargar JSON ===
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

# === 2. Preparar fecha para nombre ===
fecha_hoy = datetime.now()
if fecha_hoy.hour >= 21:
    fecha_hoy += timedelta(days=1)
fecha_archivo = fecha_hoy.strftime("%Y%m%d")

# === 3. Generar gráfico en memoria (no en disco) ===
precios = df["precio"]
horas = df["hora"]

fig, ax = plt.subplots(figsize=(10, 6))

umbral_bajo = precios.quantile(0.33)
umbral_alto = precios.quantile(0.66)
colores = [
    "green" if p <= umbral_bajo else "yellow" if p <= umbral_alto else "red"
    for p in precios
]

ax.bar(horas, precios, color=colores)
ax.axhline(precios.mean(), color="blue", linestyle="--", label="Precio medio")
ax.set_xlabel("Hora")
ax.set_ylabel("Precio (€/kWh)")
ax.set_title("PVPC Diario")
ax.legend()
plt.tight_layout()

# Guardar gráfico en memoria (BytesIO)
buffer = BytesIO()
plt.savefig(buffer, format="png")
plt.close()
buffer.seek(0)

# Codificar la imagen en base64
img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
img_tag = f'<img src="data:image/png;base64,{img_base64}" alt="Gráfico PVPC">'

# === 4. Crear HTML con imagen embebida ===
html_content = f"""
<h1>PVPC Diario</h1>
<p><strong>Estadísticas:</strong><br>
Máximo: {precios.max():.4f} €/kWh<br>
Mínimo: {precios.min():.4f} €/kWh<br>
Medio: {precios.mean():.4f} €/kWh
</p>
{df.to_html(index=False)}
<br>
{img_tag}
"""

os.makedirs("outputs", exist_ok=True)
html_file = "outputs/temp.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

# === 5. Generar PDF (ya no necesita acceso local) ===
output_pdf = f"outputs/pvpc_{fecha_archivo}.pdf"
options = {
    "quiet": ""
}

try:
    pdfkit.from_file(html_file, output_pdf, options=options)
    print(f"✅ PDF generado correctamente: {output_pdf}")
except OSError as e:
    print("❌ Error al generar el PDF:")
    print(e)
    exit(1)

# === 6. Limpieza ===
os.remove(html_file)
