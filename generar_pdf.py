import json
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from matplotlib.patches import Patch

# === 1. Cargar JSON ===
json_file = "outputs/pvpc.json"
if not os.path.exists(json_file):
    print("❌ No hay JSON de PVPC")
    exit(1)

with open(json_file, "r", encoding="utf-8") as f:
    datos = json.load(f)

df = pd.DataFrame(datos["PVPC"])

# === 2. Tomar la fecha del JSON ===
fecha_json = datos.get("fecha_publicacion")
if not fecha_json:
    print("⚠️ No se encontró 'fecha_publicacion' en el JSON. Se usará la fecha actual.")
    fecha_json = datetime.now().strftime("%Y-%m-%d")

fecha_dt = datetime.strptime(fecha_json, "%Y-%m-%d")
fecha_archivo = fecha_dt.strftime("%Y%m%d")
fecha_formateada = fecha_dt.strftime("%d/%m/%Y")

os.makedirs("outputs", exist_ok=True)
output_pdf = f"outputs/pvpc_{fecha_archivo}.pdf"

# Procesar precios y horas
precios = df["precio"]
horas_raw = df["hora"]

horas = [h.replace("-", "").replace(":00", "").zfill(2) for h in horas_raw]

precio_medio = precios.mean()
precio_max = precios.max()
precio_min = precios.min()

# === Umbrales Dinámicos Diarios (Basados en datos de REE) ===
umbral_bajo = precios.quantile(0.33)
umbral_alto = precios.quantile(0.66)

# === 3. Generación del gráfico con Matplotlib ===
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)

colores_barras = []
for p in precios:
    if p <= umbral_bajo:
        colores_barras.append('#22c55e') # Verde (Bajo)
    elif p <= umbral_alto:
        colores_barras.append('#eab308') # Amarillo plátano (Medio)
    else:
        colores_barras.append('#ef4444') # Rojo (Alto)

ax.bar(horas, precios, color=colores_barras, edgecolor='none', width=0.65)

# Línea horizontal del precio medio
ax.axhline(precio_medio, color='#1e293b', linestyle='--', linewidth=1.5, 
           label=f'Precio Medio: {precio_medio:.3f} €/kWh')

ax.set_title('Evolución Horaria de Precios PVPC', fontsize=13, fontweight='bold', pad=12, color='#1e293b')
ax.set_xlabel('Hora del Día', fontsize=11, fontweight='bold', labelpad=8, color='#1e293b')

# Ubicación de la leyenda del eje Y por encima del valor superior
ax.set_ylabel('Precio (€/kWh)', fontsize=10, fontweight='bold', labelpad=8, color='#1e293b')
ax.yaxis.set_label_coords(-0.06, 1.05)

# Tamaño de fuente aumentado en las horas del eje X
ax.set_xticks(range(len(horas)))
ax.set_xticklabels(horas, fontsize=10, fontweight='bold')
ax.tick_params(axis='y', labelsize=8)
ax.set_ylim(0, max(precios) * 1.15)

# Leyenda limpia de etiquetas únicamente (Sin rangos numéricos fijos)
legend_elements = [
    Patch(facecolor='#22c55e', label='Bajo'),
    Patch(facecolor='#eab308', label='Medio'),
    Patch(facecolor='#ef4444', label='Alto'),
    plt.Line2D([0], [0], color='#1e293b', linestyle='--', linewidth=1.5, label=f'Media ({precio_medio:.3f} €/kWh)')
]
ax.legend(handles=legend_elements, frameon=True, facecolor='white', edgecolor='none', fontsize=8, loc='upper left')

plt.tight_layout()
chart_path = os.path.abspath("outputs/temp_chart.png")
plt.savefig(chart_path, dpi=300)
plt.close()

# === 4. Construcción del PDF con ReportLab ===
doc = SimpleDocTemplate(output_pdf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
story = []

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'TitleStyle', 
    parent=styles['Heading1'], 
    fontSize=15, 
    textColor=colors.HexColor('#0f172a'), 
    spaceAfter=14, 
    alignment=1
)

heading_style = ParagraphStyle(
    'HeadingStyle', 
    parent=styles['Heading2'], 
    fontSize=12, 
    textColor=colors.HexColor('#0f172a'), 
    spaceBefore=28, 
    spaceAfter=10
)

# Título de una sola línea
story.append(Paragraph(f"<b>Informe Diario de Precios PVPC con fecha {fecha_formateada}</b>", title_style))

# Tarjetas KPI redondeadas a 3 decimales
summary_data = [
    [
        Paragraph("<b>Precio Mínimo</b>", styles['Normal']),
        Paragraph("<b>Precio Medio</b>", styles['Normal']),
        Paragraph("<b>Precio Máximo</b>", styles['Normal'])
    ],
    [
        Paragraph(f"<font size=12 color='#16a34a'><b>{precio_min:.3f} €/kWh</b></font>", styles['Normal']),
        Paragraph(f"<font size=12 color='#ca8a04'><b>{precio_medio:.3f} €/kWh</b></font>", styles['Normal']),
        Paragraph(f"<font size=12 color='#dc2626'><b>{precio_max:.3f} €/kWh</b></font>", styles['Normal'])
    ]
]
summary_table = Table(summary_data, colWidths=[170, 170, 170])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
]))
story.append(summary_table)
story.append(Spacer(1, 12))

# Gráfico
story.append(Image(chart_path, width=510, height=230))

# Desglose Horario
story.append(Paragraph("<b>Desglose Horario Detallado</b>", heading_style))

table_data = [["Hora", "Precio (€/kWh)", "Hora", "Precio (€/kWh)"]]

# Función de formato con colores según los cuantiles del día
def format_price(val):
    val_str = f"{val:.4f} €/kWh"
    if val <= umbral_bajo:
        return f"<font color='#16a34a'><b>{val_str}</b></font>"
    elif val <= umbral_alto:
        return f"<font color='#ca8a04'><b>{val_str}</b></font>"
    else:
        return f"<font color='#dc2626'><b>{val_str}</b></font>"

for i in range(12):
    row = [
        f"{horas[i]}:00",
        Paragraph(format_price(precios[i]), styles['Normal']),
        f"{horas[i+12]}:00",
        Paragraph(format_price(precios[i+12]), styles['Normal'])
    ]
    table_data.append(row)

hourly_table = Table(table_data, colWidths=[90, 165, 90, 165])
hourly_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 9),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('TOPPADDING', (0,0), (-1,0), 6),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0'))
]))
story.append(hourly_table)

# Compilar PDF
doc.build(story)

# Limpieza
try:
    os.remove(chart_path)
except Exception as e:
    print(f"⚠️ Limpieza incompleta: {e}")

print(f"✅ PDF generado correctamente: {output_pdf}")
