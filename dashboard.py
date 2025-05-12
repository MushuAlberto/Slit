import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

st.set_page_config(layout="wide")
st.title("Tablero Despachos - Informe Operacional 2025")

def verificar_datos(df, columnas):
    if df.empty:
        return False
    if not all(col in df.columns for col in columnas):
        return False
    if df["Fecha"].nunique() < 1:
        return False
    for col in columnas:
        if df[col].notna().sum() < 1:
            return False
    return True

def crear_pdf_con_grafico_reportlab(fig, titulo):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Logo
    try:
        logo = ImageReader("image.png")
        c.drawImage(logo, 40, height - 80, width=100, preserveAspectRatio=True, mask='auto')
    except:
        pass

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, titulo)

    # Convertir gráfico a imagen PNG en memoria
    img_bytes = fig.to_image(format="png", width=600, height=400, scale=2)
    img_buffer = io.BytesIO(img_bytes)
    img = ImageReader(img_buffer)

    # Dibujar imagen del gráfico
    c.drawImage(img, 40, height - 480, width=520, height=360)

    # Pie de página con fecha
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, 30, f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def crear_pdf_completo_reportlab(figs, titulos):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    try:
        logo = ImageReader("image.png")
    except:
        logo = None

    for fig, titulo in zip(figs, titulos):
        if logo:
            c.drawImage(logo, 40, height - 80, width=100, preserveAspectRatio=True, mask='auto')
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 50, titulo)

        img_bytes = fig.to_image(format="png", width=600, height=400, scale=2)
        img_buffer = io.BytesIO(img_bytes)
        img = ImageReader(img_buffer)

        c.drawImage(img, 40, height - 480, width=520, height=360)
        c.showPage()

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(width / 2, 30, f"Informe generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.save()
    buffer.seek(0)
    return buffer

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

        cols_numericas = [
            "Ton (Prog)", "Ton (Real)",
            "Equipos (Prog)", "Equipos (Real)",
            "Promedio Carga (Meta)", "Promedio Carga (Real)",
            "Aljibes M&Q (Prog)", "Aljibes M&Q (Real)",
            "Aljibes Jorquera (Prog)", "Aljibes Jorquera (Real)"
        ]
        for col in cols_numericas:
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

            st.subheader("Dashboard General")
            col1, col2 = st.columns(2)

            pdf_figs = []
            pdf_titles = []

            with col1:
                st.image("image.png", width=800)
                cols_ton = ["Ton (Prog)", "Ton (Real)"]
                if verificar_datos(df_filtrado, cols_ton):
                    fig_ton = px.line(df_filtrado.sort_values("Fecha"), x="Fecha", y=cols_ton, title="Tonelaje Programado vs Real") if df_filtrado["Fecha"].nunique() > 1 else px.bar(df_filtrado, x="Fecha", y=cols_ton, barmode="group", title="Tonelaje Programado vs Real (día único)")
                    st.plotly_chart(fig_ton, use_container_width=True)
                    pdf_buffer = crear_pdf_con_grafico_reportlab(fig_ton, "Tonelaje Programado vs Real")
                    st.download_button("📥 Descargar Gráfico Tonelaje (PDF)", pdf_buffer, file_name="tonelaje.pdf", mime="application/pdf")
                    pdf_figs.append(fig_ton)
                    pdf_titles.append("Tonelaje Programado vs Real")
                else:
                    st.info("No hay suficientes datos de Tonelaje para graficar.")

                st.image("image.png", width=800)
                cols_equip = ["Equipos (Prog)", "Equipos (Real)"]
                if verificar_datos(df_filtrado, cols_equip):
                    fig_equip = px.line(df_filtrado.sort_values("Fecha"), x="Fecha", y=cols_equip, title="Equipos Programados vs Reales") if df_filtrado["Fecha"].nunique() > 1 else px.bar(df_filtrado, x="Fecha", y=cols_equip, barmode="group", title="Equipos Programados vs Reales (día único)")
                    st.plotly_chart(fig_equip, use_container_width=True)
                    pdf_buffer = crear_pdf_con_grafico_reportlab(fig_equip, "Equipos Programados vs Reales")
                    st.download_button("📥 Descargar Gráfico Equipos (PDF)", pdf_buffer, file_name="equipos.pdf", mime="application/pdf")
                    pdf_figs.append(fig_equip)
                    pdf_titles.append("Equipos Programados vs Reales")
                else:
                    st.info("No hay suficientes datos de Equipos para graficar.")

            with col2:
                st.image("image.png", width=800)
                cols_prom = ["Promedio Carga (Meta)", "Promedio Carga (Real)"]
                if verificar_datos(df_filtrado, cols_prom):
                    fig_prom = px.line(df_filtrado.sort_values("Fecha"), x="Fecha", y=cols_prom, title="Promedio de Carga Programado vs Real") if df_filtrado["Fecha"].nunique() > 1 else px.bar(df_filtrado, x="Fecha", y=cols_prom, barmode="group", title="Promedio de Carga Programado vs Real (día único)")
                    st.plotly_chart(fig_prom, use_container_width=True)
                    pdf_buffer = crear_pdf_con_grafico_reportlab(fig_prom, "Promedio de Carga")
                    st.download_button("📥 Descargar Gráfico Promedio (PDF)", pdf_buffer, file_name="promedio_carga.pdf", mime="application/pdf")
                    pdf_figs.append(fig_prom)
                    pdf_titles.append("Promedio de Carga Programado vs Real")
                else:
                    st.info("No hay suficientes datos de Promedio de Carga para graficar.")

                if "Ton (Real)" in df_filtrado.columns and df_filtrado["Fecha"].nunique() > 1 and df_filtrado["Ton (Real)"].sum() > 0:
                    inicio = df_filtrado["Fecha"].min()
                    df_filtrado["Semana"] = ((df_filtrado["Fecha"] - inicio).dt.days // 7) + 1
                    st.image("image.png", width=800)
                    fig_semana = px.line(df_filtrado, x="Fecha", y="Ton (Real)", color="Semana", title="Tonelaje Real por Semana")
                    st.plotly_chart(fig_semana, use_container_width=True)
                    pdf_buffer = crear_pdf_con_grafico_reportlab(fig_semana, "Tonelaje Real por Semana")
                    st.download_button("📥 Descargar Gráfico Semana (PDF)", pdf_buffer, file_name="tonelaje_semana.pdf", mime="application/pdf")
                    pdf_figs.append(fig_semana)
                    pdf_titles.append("Tonelaje Real por Semana")
                else:
                    st.info("No hay suficientes datos de Tonelaje Real para graficar por semana.")

            if pdf_figs:
                pdf_buffer = crear_pdf_completo_reportlab(pdf_figs, pdf_titles)
                st.download_button("📥 Descargar TODOS los gráficos en un PDF", pdf_buffer, file_name="informe_completo.pdf", mime="application/pdf")

            st.markdown("---")
            st.subheader("Dashboard por Empresa")

            col3, col4 = st.columns(2)
            if empresa_aljibe in ["Ambas", "M&Q"]:
                with col3:
                    st.image("mq.png", width=120)
                    cols_mq = ["Aljibes M&Q (Prog)", "Aljibes M&Q (Real)"]
                    if verificar_datos(df_filtrado, cols_mq):
                        fig_mq = px.line(df_filtrado.sort_values("Fecha"), x="Fecha", y=cols_mq, title="Aljibes M&Q: Programados vs Reales") if df_filtrado["Fecha"].nunique() > 1 else px.bar(df_filtrado, x="Fecha", y=cols_mq, barmode="group", title="Aljibes M&Q: Programados vs Reales (día único)")
                        st.plotly_chart(fig_mq, use_container_width=True)
                        pdf_buffer = crear_pdf_con_grafico_reportlab(fig_mq, "Aljibes M&Q")
                        st.download_button("📥 Descargar Gráfico Aljibes M&Q (PDF)", pdf_buffer, file_name="aljibes_mq.pdf", mime="application/pdf")
                    else:
                        st.info("No hay suficientes datos de Aljibes M&Q para graficar.")

            if empresa_aljibe in ["Ambas", "Jorquera"]:
                with col4:
                    st.image("jorquera.png", width=120)
                    cols_jorquera = ["Aljibes Jorquera (Prog)", "Aljibes Jorquera (Real)"]
                    if verificar_datos(df_filtrado, cols_jorquera):
                        fig_jorquera = px.line(df_filtrado.sort_values("Fecha"), x="Fecha", y=cols_jorquera, title="Aljibes Jorquera: Programados vs Reales") if df_filtrado["Fecha"].nunique() > 1 else px.bar(df_filtrado, x="Fecha", y=cols_jorquera, barmode="group", title="Aljibes Jorquera: Programados vs Reales (día único)")
                        st.plotly_chart(fig_jorquera, use_container_width=True)
                        pdf_buffer = crear_pdf_con_grafico_reportlab(fig_jorquera, "Aljibes Jorquera")
                        st.download_button("📥 Descargar Gráfico Aljibes Jorquera (PDF)", pdf_buffer, file_name="aljibes_jorquera.pdf", mime="application/pdf")
                    else:
                        st.info("No hay suficientes datos de Aljibes Jorquera para graficar.")

            st.markdown("---")
            with st.expander("Mostrar datos filtrados (opcional)"):
                st.dataframe(df_filtrado)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
else:
    st.info("Por favor, sube el archivo Excel con la hoja 'Base de Datos'.")