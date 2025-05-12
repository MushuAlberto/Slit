import streamlit as st
import pandas as pd

st.title("Verificación de Columnas")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xls", "xlsx", "xlsm"])

if archivo:
    # Primero, leamos todas las columnas para ver su estructura
    df = pd.read_excel(
        archivo,
        sheet_name="Base de Datos",
        engine="openpyxl"
    )

    # Mostrar información sobre las columnas
    st.write("Nombres de todas las columnas:")
    st.write(df.columns.tolist())

    # Mostrar las primeras filas para ver los datos
    st.write("Primeras filas del archivo:")
    st.write(df.head())

    # Mostrar información sobre el DataFrame
    st.write("Información del DataFrame:")
    st.write(df.info())

else:
    st.info("Por favor, sube el archivo Excel con la hoja 'Base de Datos'.")