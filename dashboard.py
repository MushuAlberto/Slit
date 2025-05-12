import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Tablero Despachos - Informe Operacional 2025")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xls", "xlsx", "xlsm"])

if archivo:
    # Leer solo las columnas necesarias usando los nombres exactos
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

    # Convertir Fecha a datetime
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    # Filtros generales
    with st.sidebar:
        st.header("Filtros Generales")
        fechas = st.multiselect(
            "Selecciona una o más fechas",
            options=sorted(df["Fecha"].dt.date.unique()),
            default=sorted(df["Fecha"].dt.date.unique())
        )
        productos = st.multiselect(
            "Selecciona uno o más productos",
            options=sorted(df["Producto"].dropna().unique()),
            default=sorted(df["Producto"].dropna().unique())
        )
        destinos = st.multiselect(
            "Selecciona uno o más destinos",
            options=sorted(df["Destino"].dropna().unique()),
            default=sorted(df["Destino"].dropna().unique())
        )

    # Filtrar el DataFrame
    df_filtrado = df[
        df["Fecha"].dt.date.isin(fechas) &
        df["Producto"].isin(productos) &
        df["Destino"].isin(destinos)
    ]

    st.write("Cantidad de filas después de filtrar:", len(df_filtrado))
    st.write("Columnas disponibles:", df_filtrado.columns.tolist())

    if df_filtrado.empty:
        st.warning("No hay datos para los filtros seleccionados. Por favor, ajusta los filtros.")
    else:
        st.subheader("Dashboard General")

        col1, col2 = st.columns(2)
        with col1:
            fig_ton = px.line(
                df_filtrado,
                x="Fecha",
                y=["Ton (Prog)", "Ton (Real)"],
                title="Tonelaje Programado vs Real"
            )
            st.plotly_chart(fig_ton, use_container_width=True)

            fig_equip = px.line(
                df_filtrado,
                x="Fecha",
                y=["Equipos (Prog)", "Equipos (Real)"],
                title="Equipos Programados vs Reales"
            )
            st.plotly_chart(fig_equip, use_container_width=True)

        with col2:
            fig_prom = px.line(
                df_filtrado,
                x="Fecha",
                y=["Promedio Carga (Meta)", "Promedio Carga (Real)"],
                title="Promedio de Carga Programado vs Real"
            )
            st.plotly_chart(fig_prom, use_container_width=True)

            # Gráfico por semana (colores diferentes cada 7 días)
            inicio = df_filtrado["Fecha"].min()
            df_filtrado["Semana"] = ((df_filtrado["Fecha"] - inicio).dt.days // 7) + 1
            fig_semana = px.line(
                df_filtrado,
                x="Fecha",
                y="Ton (Real)",
                color="Semana",
                title="Tonelaje Real por Semana (colores diferentes)"
            )
            st.plotly_chart(fig_semana, use_container_width=True)

        st.markdown("---")
        st.subheader("Dashboard por Empresa")

        col3, col4 = st.columns(2)
        with col3:
            fig_mq = px.line(
                df_filtrado,
                x="Fecha",
                y=["Aljibes M&Q (Prog)", "Aljibes M&Q (Real)"],
                title="Aljibes M&Q: Programados vs Reales"
            )
            st.plotly_chart(fig_mq, use_container_width=True)

        with col4:
            fig_jorquera = px.line(
                df_filtrado,
                x="Fecha",
                y=["Aljibes Jorquera (Prog)", "Aljibes Jorquera (Real)"],
                title="Aljibes Jorquera: Programados vs Reales"
            )
            st.plotly_chart(fig_jorquera, use_container_width=True)

        st.markdown("---")
        st.write("Datos filtrados:", df_filtrado)

else:
    st.info("Por favor, sube el archivo Excel con la hoja 'Base de Datos'.")