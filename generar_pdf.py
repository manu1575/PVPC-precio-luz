import pandas as pd
import pdfkit
import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

os.makedirs("outputs", exist_ok=True)

# Encontrar el JSON más reciente
json_files = sorted([f for f in os.listdir("outputs") if f.endswith(".json")])
if not json_files:
    print("❌ No hay archivos JSON de PVPC")
    exit(1)

json_file = os.path.join("outputs", json_files[-1])
with open(json_file, "r", encoding="utf-8") as f:
    datos = json.load(f)

# Convertir a DataFrame
df = pd.DataFrame([
    {"Hora": d["datetime"][-8:-3], "Precio (€/MWh)": round(d["value"], 2)}
    for d in datos
])
df = df.sort_values("Hora").reset_index(drop=True)

# Gráfico de barras
precios = df["Precio (€/MWh)"]
precio_medio = precios.mean()
bajo = np.percentile(precios, 33)
alto = np.percentile(precios, 66)
colores = ["green" if p <= bajo else "gold" if p <= alto else "red" for p in precios]

plt.figure(figsize=(10,5))
plt.bar(df["Hora"], precios, color=colores, edgecolor="black")
plt.axhline(precio_medio, color="red", linestyle="--", linewidth=1.5, label=f"Media: {precio_medio:.2f} €/MWh")
plt.title("Evolución del Precio Horario PVPC", fontsize=14)
plt.xlabel("Hora", fontsize=12)
plt.ylabel("€/MWh", fontsize=12)
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
grafico_path = "outputs/pvpc_grafico.png"
plt.savefig(grafico_path)
plt.close()

# CSS
css_file = "outputs/style.css"
css_content = """
body { font-family: 'Helvetica', Arial, sans-serif; margin:20px; color:#333; }
h1 { text-align:center; color:#004aad; }
img { display:block; margin: 0 auto; max-width:100%; margin-top:20px; margin-bottom:20px; }
table { border-collapse: collapse; width: 100%; margin-top: 20px; }
th, td { border:1px solid #aaa; padding:8px; text-align:center; }
th { background-color:#004aad; color:white; font-weight:bold; }
tr:nth-child(even){ background-color:#f2f2f2; }
footer{ margin-top:30px; text-align:center; font-size:12px; color:#777; }
"""
with open(css_file,"w", encoding="utf-8") as f:
    f.write(css_content)

# HTML temporal
fecha = datetime.now().strftime("%d/%m/%Y")
html_file = "outputs/temp.html"
html_content = f"""
<html>
<head>
<meta charset="utf-8">
<title>Informe Diario PVPC</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<h1>Informe Diario PVPC - {fecha}</h1>
<img src="pvpc_grafico.png" alt="Gráfico PVPC">
{df.to_html(index=False)}
<footer>Fuente: REE - Generado automáticamente</footer>
</body>
</html>
"""
with open(html_file,"w",encoding="utf-8") as f:
    f.write(html_content)

# Generar PDF
output_pdf = f"outputs/PVPC-{datetime.now().strftime('%Y-%m-%d')}.pdf"
try:
    pdfkit.from_file(html_file, output_pdf, css=css_file)
    print(f"✅ PDF generado: {output_pdf}")
except Exception as e:
    print(f"❌ Error al generar PDF: {e}")
    exit(1)

