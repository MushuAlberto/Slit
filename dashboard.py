x
from fpdf import FPDF
import plotly.io as pio
import io
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Tablero Despachos - Informe Operacional 2025")

class PDF(FPDF):
def header(self):
self.image('image.png', 10, 8, 33)
self.set_font('Arial', 'B', 15)
self.cell(80)
self.cell(30, 10, 'Informe de Despachos', 0, 0, 'C')
self.ln(20)

def verificar_datos(df, columnas_requeridas):
if df.empty:
return False
if not all(col in df.columns for col in columnas_requeridas):
return False
if df["Fecha"].nunique() < 1:
return False
for col in columnas_requeridas:
if df[col].notna().sum() < 1:
return False
return True

def create_pdf_with_plot(fig, title):
pdf = PDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, title, ln=True, align='C')
pdf.ln(10)
img_bytes = fig.to_image(format="png", width=800, height=500, scale=2)
img_buffer = io.BytesIO(img_bytes)
pdf.image(img_buffer, x=10, y=50, w=190)
pdf.set_font('Arial', 'I', 8)
pdf.set_y(-15)
pdf.cell(0, 10, f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 0, 'C')
return pdf.output(dest='S').encode('latin-1')

def create_full_report(figs, titles):
pdf = PDF()
for fig, title in zip(figs, titles):
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, title, ln=True, align='C')
pdf.ln(10)
img_bytes = fig.to_image(format="png", width=800, height=500, scale=2)
img_buffer = io.BytesIO(img_bytes)
pdf.image(img_buffer, x=10, y=50, w=190)
pdf.set_font('Arial', 'I', 8)
pdf.set_y(-15)
pdf.cell(0, 10, f'Informe generado el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 0, 'C')
return pdf.output(dest='S').encode('latin-1')

archivo = st.file_uploader("Sube tu archivo Excel", type=["xls", "xlsx", "xlsm"])

if archivo:
try:
df = pd.read_excel(
archivo,
sheet_name="Base de Datos",
usecols=[
"Fecha", "Producto", "Destino", "Ton (Prog)", "Ton (Real)",
"Equipos (Prog)", "Equipos (Real)", "Promedio Carga (Meta)", "Promedio Carga (Real)",
"Aljibes M&Q (Prog)", "Aljibes M&Q (Real)", "Aljibes Jorquera (Prog)", "Aljibes Jorquera (Real)"
],
engine="openpyxl"
)
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df = df.dropna(subset=["Fecha"])
columnas_numericas = [
"Ton (Prog)", "Ton (Real)",
"Equipos (Prog)", "Equipos (Real)",
"Promedio Carga (Meta)", "Promedio Carga (Real)",
"Aljibes M&Q (Prog)", "Aljibes M&Q (Real)",
"Aljibes Jorquera (Prog)", "Aljibes Jorquera (Real)"
]
for col in columnas_numericas:
if col in df.columns:
df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
df = df[(df["Producto"] == "SLIT") & (df["Fecha"].dt.year >= 2025)]
if df.empty:
st.warning('No hay datos para el producto "SLIT" en el año 2025 o posterior.')
else:
with st.sidebar:
st.header("Filtros Generales")
fechas = st.multiselect(
"Selecciona una o más fechas",
options=sorted(df["Fecha"].dt.date.unique()),
default=sorted(df["Fecha"].dt.date.unique())
)
destinos = st.multiselect(
"Selecciona uno o más destinos",
options=sorted(df["Destino"].unique()),
default=sorted(df["Destino"].unique())
)
empresa_aljibe = st.selectbox(
"Selecciona empresa de aljibes a mostrar",
["Ambas", "M&Q", "Jorquera"]
)
df_filtrado = df[
df["Fecha"].dt.date.isin(fechas) &
df["Destino"].isin(destinos)
]
st.write("Cantidad de filas después de filtrar:", len(df_filtrado))
st.write("Columnas disponibles:", df_filtrado.columns.tolist())
st.subheader("Dashboard General")
col1, col2 = st.columns(2)
pdf_figs = []
pdf_titles = []
with col1:
st.image("image.png", width=800)
cols_ton = ["Ton (Prog)", "Ton (Real)"]
if verificar_datos(df_filtrado, cols_ton):
if df_filtrado["Fecha"].nunique() >= 2:
fig_ton = px.line(
df_filtrado.sort_values("Fecha"),
x="Fecha",
y=cols_ton,
title="Tonelaje Programado vs Real"
)
elif df_filtrado["Fecha"].nunique() == 1:
fig_ton = px.bar(
df_filtrado,
x="Fecha",
y=cols_ton,
barmode="group",
title="Tonelaje Programado vs Real (día único)"
)
st.plotly_chart(fig_ton, use_container_width=True)
pdf_bytes = create_pdf_with_plot(fig_ton, "Tonelaje Programado vs Real")
st.download_button(
label="📥 Descargar Gráfico Tonelaje (PDF)",
data=pdf_bytes,
file_name=f"tonelaje_{datetime.now().strftime('%Y%m%d')}.pdf",
mime="application/pdf"
)
pdf_figs.append(fig_ton)
pdf_titles.append("Tonelaje Programado vs Real")
else:
st.info("No hay suficientes datos de Tonelaje para graficar.")
st.image("image.png", width=800)
cols_equip = ["Equipos (Prog)", "Equipos (Real)"]
if verificar_datos(df_filtrado, cols_equip):
if df_filtrado["Fecha"].nunique() >= 2:
fig_equip = px.line(
df_filtrado.sort_values("Fecha"),
x="Fecha",
y=cols_equip,
title="Equipos Programados vs Reales"
)
elif df_filtrado["Fecha"].nunique() == 1:
fig_equip = px.bar(
df_filtrado,
x="Fecha",
y=cols_equip,
barmode="group",
title="Equipos Programados vs Reales (día único)"
)
st.plotly_chart(fig_equip, use_container_width=True)
pdf_bytes = create_pdf_with_plot(fig_equip, "Equipos Programados vs Reales")
st.download_button(
label="📥 Descargar Gráfico Equipos (PDF)",
data=pdf_bytes,
file_name=f"equipos_{datetime.now().strftime('%Y%m%d')}.pdf",
mime="application/pdf"
)
pdf_figs.append(fig_equip)
pdf_titles.append("Equipos Programados vs Reales")
else:
st.info("No hay suficientes datos de Equipos para graficar.")
with col2:
st.image("image.png", width=800)
cols_prom = ["Promedio Carga (Meta)", "Promedio Carga (Real)"]
if verificar_datos(df_filtrado, cols_prom):
if df_filtrado["Fecha"].nunique() >= 2:
fig_prom = px.line(
df_filtrado.sort_values("Fecha"),
x="Fecha",
y=cols_prom,
title="Promedio de Carga Programado vs Real"
)
elif df_filtrado["Fecha"].nunique() == 1:
fig_prom = px.bar(
df_filtrado,
x="Fecha",
y=cols_prom,
barmode="group",
title="Promedio de Carga Programado vs Real (día único)"
)
st.plotly_chart(fig_prom, use_container_width=True)
pdf_bytes = create_pdf_with_plot(fig_prom, "Promedio de Carga")
st.download_button(
label="📥 Descargar Gráfico Promedio (PDF)",
data=pdf_bytes,
file_name=f"promedio_{datetime.now().strftime('%Y%m%d')}.pdf",
mime="application/pdf"
)
pdf_figs.append(fig_prom)
pdf_titles.append("Promedio de Carga Programado vs Real")
else:
st.info("No hay suficientes datos de Promedio de Carga para graficar.")
if (
"Ton (Real)" in df_filtrado.columns and
df_filtrado["Fecha"].nunique() >= 2 and
df_filtrado["Ton (Real)"].sum() > 0
):
inicio = df_filtrado["Fecha"].min()
df_filtrado["Semana"] = ((df_filtrado["Fecha"] - inicio).dt.days // 7) + 1
st.image("image.png", width=800)
fig_semana = px.line(
df_filtrado,
x="Fecha",
y="Ton (Real)",
color="Semana",
title="Tonelaje Real por Semana"
)
st.plotly_chart(fig_semana, use_container_width=True)
pdf_bytes = create_pdf_with_plot(fig_semana, "Tonelaje por Semana")
st.download_button(
label="📥 Descargar Gráfico Semana (PDF)",
data=pdf_bytes,
file_name=f"semana_{datetime.now().strftime('%Y%m%d')}.pdf",
mime="application/pdf"
)
pdf_figs.append(fig_semana)
pdf_titles.append("Tonelaje Real por Semana")
else:
st.info("No hay suficientes datos de Tonelaje Real para graficar por semana.")
if pdf_figs:
pdf_bytes = create_full_report(pdf_figs, pdf_titles)
st.download_button(
label="📥 Descargar TODOS los gráficos en un PDF",
data=pdf_bytes,
file_name=f"informe_completo_{datetime.now().strftime('%Y%m%d')}.pdf",
mime="application/pdf"
)
st.markdown("---")
st.subheader("Dashboard por Empresa")
col3, col4 = st.columns(2)
if empresa_aljibe in ["Ambas", "M&Q"]:
with col3:
st.image("mq.png", width=120)
cols_mq = ["Aljibes M&Q (Prog)", "Aljibes M&Q (Real)"]
if verificar_datos(df_filtrado, cols_mq):
fig_mq = None
if df_filtrado["Fecha"].nunique() >= 2:
fig_mq = px.line(
df_filtrado.sort_values("Fecha"),
x="Fecha",
y=cols_mq,
title="Aljibes M&Q: Programados vs Reales"
)
elif df_filtrado["Fecha"].nunique() == 1:
fig_mq = px.bar(
df_filtrado,
x="Fecha",
y=cols_mq,
barmode="group",
title="Aljibes M&Q: Programados vs Reales (día único)"
)
if fig_mq:
st.plotly_chart(fig_mq, use_container_width=True)
pdf_bytes = create_pdf_with_plot(fig_mq, "Aljibes M&Q")
st.download_button(
label="📥 Descargar Gráfico Aljibes M&Q (PDF)",
data=pdf_bytes,
file_name=f"aljibes_mq_{datetime.now().strftime('%Y%m%d')}.pdf",
mime="application/pdf"
)
else:
st.info("No hay suficientes datos de Aljibes M&Q para graficar.")
if empresa_aljibe in ["Ambas", "Jorquera"]:
with col4:
st.image("jorquera.png", width=120)
cols_jorquera = ["Aljibes Jorquera (Prog)", "Aljibes Jorquera (Real)"]
if verificar_datos(df_filtrado, cols_jorquera):
fig_jorquera = None
if df_filtrado["Fecha"].nunique() >= 2:
fig_jorquera = px.line(
df_filtrado.sort_values("Fecha"),
x="Fecha",
y=cols_jorquera,
title="Aljibes Jorquera: Programados vs Reales"
)
elif df_filtrado["Fecha"].nunique() == 1:
fig_jorquera = px.bar(
df_filtrado,
x="Fecha",
y=cols_jorquera,
barmode="group",
title="Aljibes Jorquera: Programados vs Reales (día único)"
)
if fig_jorquera:
st.plotly_chart(fig_jorquera, use_container_width=True)
pdf_bytes = create_pdf_with_plot(fig_jorquera, "Aljibes Jorquera")
st.download_button(
label="📥 Descargar Gráfico Aljibes Jorquera (PDF)",
data=pdf_bytes,
file_name=f"aljibes_jorquera_{datetime.now().strftime('%Y%m%d')}.pdf",
mime="application/pdf"
)
else:
st.info("No hay suficientes datos de Aljibes Jorquera para graficar.")
st.markdown("---")
with st.expander("Mostrar datos filtrados (opcional)"):
st.dataframe(df_filtrado)
except Exception as e:
st.error(f"Error al procesar el archivo: {str(e)}")
else:
st.info("Por favor, sube el archivo Excel con la hoja 'Base de Datos'.")
"""

codigo_lines = []
for line in codigo.split('\n'):
codigo_lines.extend(textwrap.wrap(line, width=100, replace_whitespace=False) or [''])

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Courier", size=8)

for line in codigo_lines:
pdf.cell(0, 4, line, ln=1)

pdf.output("dashboard_streamlit_completo.pdf")
print("dashboard_streamlit_completo.pdf generado")