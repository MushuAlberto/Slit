import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Dashboard de Despachos por Empresa")

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel(
            "05.- Histórico Romanas.xlsx",
            usecols=["FECHA", "PRODUCTO", "EMPRESA DE TRANSPORTE", "TONELAJE"],
            parse_dates=["FECHA"]
        )
        # Filtrar solo SLIT y limpiar datos
        df = df[df["PRODUCTO"] == "SLIT"].copy()
        df["EMPRESA"] = df["EMPRESA DE TRANSPORTE"].str.upper()
        df = df.dropna(subset=["FECHA", "TONELAJE"])
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return pd.DataFrame()

df = cargar_datos()

if not df.empty:
    with st.sidebar:
        st.header("Filtros")
        fecha_min = df["FECHA"].min().date()
        fecha_max = df["FECHA"].max().date()

        rango_fechas = st.date_input(
            "Seleccione rango de fechas",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max
        )

        empresas = sorted(df["EMPRESA"].unique())
        empresa_seleccionada = st.selectbox(
            "Seleccione empresa transportista",
            empresas
        )

    # Filtrar por fecha y empresa
    if len(rango_fechas) == 2:
        df_filtrado = df[
            (df["FECHA"].dt.date >= rango_fechas[0]) &
            (df["FECHA"].dt.date <= rango_fechas[1]) &
            (df["EMPRESA"] == empresa_seleccionada)
        ]

        if not df_filtrado.empty:
            # Agrupar por día
            df_agrupado = df_filtrado.groupby(df_filtrado["FECHA"].dt.date).agg({
                "TONELAJE": "sum",
                "EMPRESA": "count"
            }).rename(columns={"EMPRESA": "CANTIDAD_EQUIPOS"}).reset_index()

            # Crear gráfico combinado
            fig = px.bar(
                df_agrupado,
                x="FECHA",
                y="TONELAJE",
                title=f"Despachos de {empresa_seleccionada} - Tonelaje (barras) vs Cantidad de Equipos (línea)",
                labels={"TONELAJE": "Tonelaje (ton)", "FECHA": "Fecha"}
            )

            # Agregar línea para cantidad de equipos
            fig.add_scatter(
                x=df_agrupado["FECHA"],
                y=df_agrupado["CANTIDAD_EQUIPOS"],
                name="Cantidad de Equipos",
                line=dict(color="red"),
                yaxis="y2"
            )

            # Configurar eje secundario
            fig.update_layout(
                yaxis2=dict(
                    title="Cantidad de Equipos",
                    overlaying="y",
                    side="right"
                ),
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Mostrar tabla resumen
            with st.expander("Ver datos detallados"):
                st.dataframe(df_agrupado)
        else:
            st.warning("No hay datos para los filtros seleccionados")
    else:
        st.warning("Seleccione un rango de fechas válido")
else:
    st.error("No se pudieron cargar los datos del archivo")