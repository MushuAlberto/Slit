import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Tablero Despachos - Informe Operacional 2025")

def verificar_datos(df, columnas_requeridas):
    """Verifica si hay suficientes datos para graficar"""
    if df.empty:
        return False
    if df["Fecha"].nunique() < 2:
        return False
    # Verificar que todas las columnas existan y tengan al menos un valor no nulo
    for col in columnas_requeridas:
        if col not in df.columns:
            return False
        if df[col].notna().sum() < 1:
            return False
    return True

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

        # Mostrar información del DataFrame original
        st.write("Información del DataFrame original:")
        st.write(f"Filas totales: {len(df)}")
        st.write("Columnas disponibles:", df.columns.tolist())

        # Convertir Fecha a datetime y eliminar filas sin fecha
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df = df.dropna(subset=["Fecha"])
        st.write(f"Filas después de eliminar fechas inválidas: {len(df)}")

        # Reemplazar NaN por 0 en columnas numéricas
        columnas_numericas = df.select_dtypes(include=['float64', 'int64']).columns
        df[columnas_numericas] = df[columnas_numericas].fillna(0)

        # Filtrar por SLIT y año 2025
        df = df[(df["Producto"] == "SLIT") & (df["Fecha"].dt.year >= 2025)]
        st.write(f"Filas después de filtrar por SLIT y año 2025: {len(df)}")

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

            # Aplicar filtros
            df_filtrado = df[
                df["Fecha"].dt.date.isin(fechas) &
                df["Destino"].isin(destinos)
            ]

            st.write("Información después de filtrar:")
            st.write(f"Filas: {len(df_filtrado)}")
            st.write(f"Fechas únicas: {df_filtrado['Fecha'].nunique()}")

            if len(df_filtrado) < 2:
                st.warning("No hay suficientes datos después de aplicar los filtros.")
            else:
                st.subheader("Dashboard General")

                col1, col2 = st.columns(2)
                with col1:
                    # Tonelaje
                    cols_ton = ["Ton (Prog)", "Ton (Real)"]
                    if verificar_datos(df_filtrado, cols_ton):
                        try:
                            fig_ton = px.line(
                                df_filtrado.sort_values("Fecha"),  # Ordenar por fecha
                                x="Fecha",
                                y=cols_ton,
                                title="Tonelaje Programado vs Real"
                            )
                            st.plotly_chart(fig_ton, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error al crear gráfico de Tonelaje: {str(e)}")
                    else:
                        st.info("No hay suficientes datos de Tonelaje para graficar.")

                    # Equipos
                    cols_equip = ["Equipos (Prog)", "Equipos (Real)"]
                    if verificar_datos(df_filtrado, cols_equip):
                        try:
                            fig_equip = px.line(
                                df_filtrado.sort_values("Fecha"),
                                x="Fecha",
                                y=cols_equip,
                                title="Equipos Programados vs Reales"
                            )
                            st.plotly_chart(fig_equip, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error al crear gráfico de Equipos: {str(e)}")
                    else:
                        st.info("No hay suficientes datos de Equipos para graficar.")

                with col2:
                    # Promedio de carga
                    cols_prom = ["Promedio Carga (Meta)", "Promedio Carga (Real)"]
                    if verificar_datos(df_filtrado, cols_prom):
                        try:
                            fig_prom = px.line(
                                df_filtrado.sort_values("Fecha"),
                                x="Fecha",
                                y=cols_prom,
                                title="Promedio de Carga Programado vs Real"
                            )
                            st.plotly_chart(fig_prom, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error al crear gráfico de Promedio de Carga: {str(e)}")
                    else:
                        st.info("No hay suficientes datos de Promedio de Carga para graficar.")

                st.markdown("---")
                st.subheader("Dashboard por Empresa")

                col3, col4 = st.columns(2)
                with col3:
                    cols_mq = ["Aljibes M&Q (Prog)", "Aljibes M&Q (Real)"]
                    if verificar_datos(df_filtrado, cols_mq):
                        try:
                            fig_mq = px.line(
                                df_filtrado.sort_values("Fecha"),
                                x="Fecha",
                                y=cols_mq,
                                title="Aljibes M&Q: Programados vs Reales"
                            )
                            st.plotly_chart(fig_mq, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error al crear gráfico de Aljibes M&Q: {str(e)}")
                    else:
                        st.info("No hay suficientes datos de Aljibes M&Q para graficar.")

                with col4:
                    cols_jorquera = ["Aljibes Jorquera (Prog)", "Aljibes Jorquera (Real)"]
                    if verificar_datos(df_filtrado, cols_jorquera):
                        try:
                            fig_jorquera = px.line(
                                df_filtrado.sort_values("Fecha"),
                                x="Fecha",
                                y=cols_jorquera,
                                title="Aljibes Jorquera: Programados vs Reales"
                            )
                            st.plotly_chart(fig_jorquera, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error al crear gráfico de Aljibes Jorquera: {str(e)}")
                    else:
                        st.info("No hay suficientes datos de Aljibes Jorquera para graficar.")

                # Mostrar datos filtrados
                st.markdown("---")
                st.subheader("Datos Filtrados")
                st.dataframe(df_filtrado)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
else:
    st.info("Por favor, sube el archivo Excel con la hoja 'Base de Datos'.")