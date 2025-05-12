import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Dashboard de Tonelaje y Equipos por Empresa")

# Función para normalizar nombres de empresas
def normalizar_empresas(df, col_empresa='EMPRESA DE TRANSPORTE'):
    empresa_mapping = {
        "JORQUERA TRANSPORTE S A": "JORQUERA TRANSPORTE S. A.",
        "MINING SERVICES AND DERIVATES": "M S & D SPA",
        "MINING SERVICES AND DERIVATES SPA": "M S & D SPA",
        "M S AND D": "M S & D SPA",
        "M S AND D SPA": "M S & D SPA",
        "MSANDD SPA": "M S & D SPA",
        "M S D": "M S & D SPA",
        "M S D SPA": "M S & D SPA",
        "M S & D": "M S & D SPA",
        "M S & D SPA": "M S & D SPA",
        "MS&D SPA": "M S & D SPA",
        "M AND Q SPA": "M&Q SPA",
        "M AND Q": "M&Q SPA",
        "M Q SPA": "M&Q SPA",
        "MQ SPA": "M&Q SPA",
        "M&Q SPA": "M&Q SPA",
        "MANDQ SPA": "M&Q SPA",
        "MINING AND QUARRYING SPA": "M&Q SPA",
        "MINING AND QUARRYNG SPA": "M&Q SPA",
        "AG SERVICE SPA": "AG SERVICES SPA",
        "AG SERVICES SPA": "AG SERVICES SPA",
        "COSEDUCAM S A": "COSEDUCAM S A",
        "COSEDUCAM": "COSEDUCAM S A"
    }
    if col_empresa in df.columns:
        df[col_empresa] = df[col_empresa].str.strip().str.upper().map(empresa_mapping).fillna(df[col_empresa])
    return df

# Carga primer archivo (05.- Histórico Romanas.xlsx)
st.sidebar.header("Carga archivo Histórico Romanas")
archivo_historico = st.sidebar.file_uploader("Sube '05.- Histórico Romanas.xlsx'", type=["xls", "xlsx", "xlsm"], key="historico")

# Carga segundo archivo para sumatoria diaria
st.sidebar.header("Carga archivo para sumatoria diaria")
archivo_sumatoria = st.sidebar.file_uploader("Sube archivo Excel para sumatoria diaria", type=["xls", "xlsx", "xlsm"], key="sumatoria")

# Procesamiento del archivo histórico
if archivo_historico is not None:
    try:
        # Leer todas las columnas primero para verificar qué columnas existen
        df_hist = pd.read_excel(archivo_historico)

        # Verificar columnas disponibles
        columnas_disponibles = df_hist.columns.tolist()
        columnas_necesarias = ['FECHA', 'PRODUCTO', 'TONELAJE']

        # Verificar si las columnas necesarias existen
        if not all(col in columnas_disponibles for col in columnas_necesarias):
            st.error(f"El archivo histórico no contiene las columnas necesarias. Columnas encontradas: {columnas_disponibles}")
        else:
            # Seleccionar solo las columnas que existen
            columnas_a_usar = [col for col in ['FECHA', 'PRODUCTO', 'TONELAJE', 'EMPRESA DE TRANSPORTE', 'EQUIPOS']
                             if col in columnas_disponibles]

            df_hist = df_hist[columnas_a_usar]
            df_hist["FECHA"] = pd.to_datetime(df_hist["FECHA"], errors="coerce")
            df_hist = df_hist.dropna(subset=["FECHA"])

            # Normalizar empresas si la columna existe
            if 'EMPRESA DE TRANSPORTE' in df_hist.columns:
                df_hist = normalizar_empresas(df_hist)

            df_hist = df_hist[df_hist["PRODUCTO"].str.strip().str.upper() == "SLIT"]

            # Dashboard combinado tonelaje y equipos por empresa
            st.header("Gráfico combinado: Tonelaje y Cantidad de Equipos por Empresa")

            if 'EMPRESA DE TRANSPORTE' in df_hist.columns:
                empresas = sorted(df_hist["EMPRESA DE TRANSPORTE"].unique())
                empresa_seleccionada = st.selectbox("Selecciona empresa para gráfico combinado", empresas)
                df_filtrado_hist = df_hist[df_hist["EMPRESA DE TRANSPORTE"] == empresa_seleccionada]
            else:
                st.warning("No se encontró la columna 'EMPRESA DE TRANSPORTE' en el archivo histórico")
                df_filtrado_hist = df_hist

            if not df_filtrado_hist.empty:
                # Verificar si existe la columna EQUIPOS
                if 'EQUIPOS' in df_filtrado_hist.columns:
                    df_agg = df_filtrado_hist.groupby(df_filtrado_hist["FECHA"].dt.date).agg({
                        "TONELAJE": "sum",
                        "EQUIPOS": "sum"
                    }).reset_index().rename(columns={"FECHA": "Fecha"})

                    fig_comb = px.bar(df_agg, x="Fecha", y="TONELAJE", labels={"TONELAJE": "Tonelaje (ton)"},
                                     title=f"Tonelaje (barras) y Equipos (línea) - {empresa_seleccionada if 'EMPRESA DE TRANSPORTE' in df_hist.columns else 'General'}")
                    fig_comb.add_scatter(x=df_agg["Fecha"], y=df_agg["EQUIPOS"], mode="lines+markers",
                                        name="Cantidad de Equipos", yaxis="y2")

                    fig_comb.update_layout(
                        yaxis2=dict(
                            title="Cantidad de Equipos",
                            overlaying="y",
                            side="right"
                        ),
                        xaxis_title="Fecha",
                        yaxis_title="Tonelaje (ton)",
                        legend=dict(y=1, x=1),
                        hovermode="x unified"
                    )
                else:
                    df_agg = df_filtrado_hist.groupby(df_filtrado_hist["FECHA"].dt.date).agg({
                        "TONELAJE": "sum"
                    }).reset_index().rename(columns={"FECHA": "Fecha"})

                    fig_comb = px.bar(df_agg, x="Fecha", y="TONELAJE", labels={"TONELAJE": "Tonelaje (ton)"},
                                     title=f"Tonelaje - {empresa_seleccionada if 'EMPRESA DE TRANSPORTE' in df_hist.columns else 'General'}")

                st.plotly_chart(fig_comb, use_container_width=True)
            else:
                st.info("No hay datos para la empresa seleccionada en el archivo histórico.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo histórico: {str(e)}")

# Procesamiento del archivo de sumatoria diaria
if archivo_sumatoria is not None:
    try:
        df_sum = pd.read_excel(archivo_sumatoria)

        # Verificar si existe la columna 'EMPRESA DE TRANSPORTE'
        if 'EMPRESA DE TRANSPORTE' in df_sum.columns:
            df_sum = normalizar_empresas(df_sum)

            # Filtrar y procesar si la columna 'PRODUCTO' existe
            if 'PRODUCTO' in df_sum.columns:
                df_sum = df_sum[df_sum['PRODUCTO'].str.strip().str.upper() == 'SLIT'].copy()

            df_sum['FECHA'] = pd.to_datetime(df_sum['FECHA'], dayfirst=True)

            st.header("Gráfico sumatoria diaria de tonelaje por empresa con tonelaje programado")

            empresas_sum = sorted(df_sum['EMPRESA DE TRANSPORTE'].unique())
            empresas_seleccionadas = st.multiselect("Selecciona Empresas (sumatoria diaria)", empresas_sum, default=empresas_seleccionadas)

            fechas_sum = sorted(df_sum['FECHA'].dt.date.unique())
            fechas_seleccionadas = st.multiselect("Selecciona Fechas (sumatoria diaria)", fechas_sum, default=fechas_seleccionadas)

            df_filtrado_sum = df_sum[
                (df_sum['EMPRESA DE TRANSPORTE'].isin(empresas_seleccionadas)) &
                (df_sum['FECHA'].dt.date.isin(fechas_seleccionadas))
            ]

            if not df_filtrado_sum.empty:
                df_grouped = df_filtrado_sum.groupby(['FECHA', 'EMPRESA DE TRANSPORTE'])['TONELAJE'].sum().reset_index()

                tonelaje_programado = 1197

                fig_sum = go.Figure()

                for empresa in df_grouped['EMPRESA DE TRANSPORTE'].unique():
                    df_emp = df_grouped[df_grouped['EMPRESA DE TRANSPORTE'] == empresa]
                    fig_sum.add_trace(go.Bar(
                        x=df_emp['FECHA'],
                        y=df_emp['TONELAJE'],
                        name=f'Real - {empresa}'
                    ))

                fechas_sorted = sorted(df_grouped['FECHA'].unique())
                fig_sum.add_trace(go.Scatter(
                    x=fechas_sorted,
                    y=[tonelaje_programado] * len(fechas_sorted),
                    mode='lines',
                    name='Tonelaje Programado (1197)',
                    line=dict(color='red', dash='dash')
                ))

                fig_sum.update_layout(
                    title='Sumatoria Diaria de Tonelaje por Empresa (Producto SLIT) vs Tonelaje Programado',
                    xaxis_title='Fecha',
                    yaxis_title='Tonelaje (ton)',
                    barmode='group',
                    height=600
                )

                st.plotly_chart(fig_sum, use_container_width=True)

                with st.expander("Ver datos detallados sumatoria diaria"):
                    st.dataframe(df_grouped)
            else:
                st.info("No hay datos para los filtros seleccionados en sumatoria diaria.")
        else:
            st.error("El archivo de sumatoria no contiene la columna 'EMPRESA DE TRANSPORTE'")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo de sumatoria diaria: {str(e)}")

if archivo_historico is None and archivo_sumatoria is None:
    st.info("Por favor, sube al menos uno de los archivos Excel para comenzar.")