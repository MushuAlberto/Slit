import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Tablero Despachos - Informe Operacional 2025")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xls", "xlsx", "xlsm"])

if archivo:
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

    # Filtrar SOLO filas donde Producto es "SLIT"
    df = df[df["Producto"] == "SLIT"]

    # Filtrar SOLO datos desde el año 2025 en adelante
    df = df[df["Fecha"].dt.year >= 2025]

    if df.empty:
        st.warning('No hay datos para el producto "SLIT" en el año 2025 o posterior en el archivo cargado.')
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
                options=sorted(df["Destino"].dropna().unique()),
                default=sorted(df["Destino"].dropna().unique())
            )

        # Aplicar filtros
        df_filtrado = df[
            df["Fecha"].dt.date.isin(fechas) &
            df["Destino"].isin(destinos)
        ]

        st.write("Cantidad de filas después de filtrar:", len(df_filtrado))
        st.write("Columnas disponibles:", df_filtrado.columns.tolist())

        if df_filtrado.shape[0] < 2:
            st.warning("No hay suficientes datos para graficar (se requiere al menos 2 filas después de filtrar). Ajusta los filtros.")
        else:
            st.subheader("Dashboard General")

            col1, col2 = st.columns(2)
            with col1:
                # Tonelaje
                cols_ton = ["Ton (Prog)", "Ton (Real)"]
                cols_ton_validas = [c for c in cols_ton if c in df_filtrado.columns and df_filtrado[c].notna().sum() > 1]
                st.write("Columnas de Tonelaje a graficar:", cols_ton_validas)
                for c in cols_ton:
                    st.write(f"{c}: {df_filtrado[c].notna().sum()} datos válidos")
                if len(cols_ton_validas) > 0:
                    fig_ton = px.line(
                        df_filtrado,
                        x="Fecha",
                        y=cols_ton_validas,
                        title="Tonelaje Programado vs Real"
                    )
                    st.plotly_chart(fig_ton, use_container_width=True)
                else:
                    st.info("No hay suficientes datos de Tonelaje para graficar.")

                # Equipos
                cols_equip = ["Equipos (Prog)", "Equipos (Real)"]
                cols_equip_validas = [c for c in cols_equip if c in df_filtrado.columns and df_filtrado[c].notna().sum() > 1]
                st.write("Columnas de Equipos a graficar:", cols_equip_validas)
                for c in cols_equip:
                    st.write(f"{c}: {df_filtrado[c].notna().sum()} datos válidos")
                if len(cols_equip_validas) > 0:
                    fig_equip = px.line(
                        df_filtrado,
                        x="Fecha",
                        y=cols_equip_validas,
                        title="Equipos Programados vs Reales"
                    )
                    st.plotly_chart(fig_equip, use_container_width=True)
                else:
                    st.info("No hay suficientes datos de Equipos para graficar.")

            with col2:
                # Promedio de carga
                cols_prom = ["Promedio Carga (Meta)", "Promedio Carga (Real)"]
                cols_prom_validas = [c for c in cols_prom if c in df_filtrado.columns and df_filtrado[c].notna().sum() > 1]
                st.write("Columnas de Promedio de Carga a graficar:", cols_prom_validas)
                for c in cols_prom:
                    st.write(f"{c}: {df_filtrado[c].notna().sum()} datos válidos")
                if len(cols_prom_validas) > 0:
                    fig_prom = px.line(
                        df_filtrado,
                        x="Fecha",
                        y=cols_prom_validas,
                        title="Promedio de Carga Programado vs Real"
                    )
                    st.plotly_chart(fig_prom, use_container_width=True)
                else:
                    st.info("No hay suficientes datos de Promedio de Carga para graficar.")

                # Gráfico por semana (colores diferentes cada 7 días)
                inicio = df_filtrado["Fecha"].min()
                df_filtrado["Semana"] = ((df_filtrado["Fecha"] - inicio).dt.days // 7) + 1
                if "Ton (Real)" in df_filtrado.columns and df_filtrado["Ton (Real)"].notna().sum() > 1:
                    fig_semana = px.line(
                        df_filtrado,
                        x="Fecha",
                        y="Ton (Real)",
                        color="Semana",
                        title="Tonelaje Real por Semana (colores diferentes)"
                    )
                    st.plotly_chart(fig_semana, use_container_width=True)
                else:
                    st.info("No hay suficientes datos de Tonelaje Real para graficar por semana.")

            st.markdown("---")
            st.subheader("Dashboard por Empresa")

            col3, col4 = st.columns(2)
            with col3:
                cols_mq = ["Aljibes M&Q (Prog)", "Aljibes M&Q (Real)"]
                cols_mq_validas = [c for c in cols_mq if c in df_filtrado.columns and df_filtrado[c].notna().sum() > 1]
                st.write("Columnas de Aljibes M&Q a graficar:", cols_mq_validas)
                for c in cols_mq:
                    st.write(f"{c}: {df_filtrado[c].notna().sum()} datos válidos")
                if len(cols_mq_validas) > 0:
                    fig_mq = px.line(
                        df_filtrado,
                        x="Fecha",
                        y=cols_mq_validas,
                        title="Aljibes M&Q: Programados vs Reales"
                    )
                    st.plotly_chart(fig_mq, use_container_width=True)
                else:
                    st.info("No hay suficientes datos de Aljibes M&Q para graficar.")

            with col4:
                cols_jorquera = ["Aljibes Jorquera (Prog)", "Aljibes Jorquera (Real)"]
                cols_jorquera_validas = [c for c in cols_jorquera if c in df_filtrado.columns and df_filtrado[c].notna().sum() > 1]
                st.write("Columnas de Aljibes Jorquera a graficar:", cols_jorquera_validas)
                for c in cols_jorquera:
                    st.write(f"{c}: {df_filtrado[c].notna().sum()} datos válidos")
                if len(cols_jorquera_validas) > 0:
                    fig_jorquera = px.line(
                        df_filtrado,
                        x="Fecha",
                        y=cols_jorquera_validas,
                        title="Aljibes Jorquera: Programados vs Reales"
                    )
                    st.plotly_chart(fig_jorquera, use_container_width=True)
                else:
                    st.info("No hay suficientes datos de Aljibes Jorquera para graficar.")

            st.markdown("---")
            st.write("Datos filtrados:", df_filtrado)

else:
    st.info("Por favor, sube el archivo Excel con la hoja 'Base de Datos'.")