import json
import pandas as pd
import matplotlib.pyplot as plt
import pdfkit
import os

# Archivo JSON fijo
json_file = "outputs/pvpc.json"
if not os.path.exists(json_file):
    print("❌ No hay archivos JSON de PVPC")
    exit(1)

# Leer JSON
with open(json_file, "r", encoding="utf-8") as f:
    datos = json.load(f)

# Suponiendo que los precios estén en datos["PVPC"] (ajustar según estructura real)
# Crear DataFrame con horas y precios
try:
    df = pd.DataFrame(datos["PVPC"])
except KeyError:
    print("❌ La estructura JSON no contiene 'PVPC'")
    exit(1)

# Crear gráfico de barras con línea de precio medio
fig, ax = plt.subplots(figsize=(10,6))
precios = df["precio"]  # Ajustar según clave real
horas = df["hora"]

# Colorear según precio
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
ax.set_ylabel("Precio (€)")
ax.set_title("PVPC Diario")
ax.legend()

# Guardar gráfico como HTML para PDF
os.makedirs("outputs", exist_ok=True)
html_file = "outputs/temp.html"
plt.savefig("outputs/temp.png")  # Opcional: guardar imagen también
plt.close()

# Generar HTML simple
html_content = df.to_html(index=False)
with open(html_file, "w", encoding="utf-8") as f:
    f.write(f"<h1>PVPC Diario</h1>\n{html_content}\n<img src='temp.png'>")

# Generar PDF
output_pdf = "outputs/pvpc_diario.pdf"
pdfkit.from_file(html_file, output_pdf)
print(f"✅ PDF generado en {output_pdf}")

