import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.dataset_utils import *

st.set_page_config(
    page_title="Datasets",
    page_icon="📂"
)
st.title("Datasets disponibles")

directorio = Path(__file__).parent.parent / "processed_datasets"

datos = []
for archivo in directorio.glob("*.csv"):
    stat = archivo.stat()
    datos.append({
        "Nombre": archivo.name,
        "Tamaño (MB)": round(stat.st_size / (1024 * 1024), 4),
        "Última modificación": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    })

if datos:
    st.dataframe(datos, use_container_width=True, hide_index=True)
else:
    st.warning("No hay datasets disponibles en processed_datasets/")

st.divider()
st.subheader("Detalle de dataset")

if datos:
    nombres = [d["Nombre"] for d in datos]
    seleccionado = st.selectbox("Seleccioná un dataset para ver su detalle", nombres)

    try:
        sep = detectar_separador(directorio / seleccionado)
        df = pd.read_csv(directorio / seleccionado, sep=sep, encoding="utf-8", on_bad_lines="skip")

        st.metric("Total de registros", len(df))
    
        st.write("Porcentaje de valores nulos por columna:")
        if len(df) > 0:
            nulos = (df.isna().sum() / len(df) * 100).round(2).reset_index()
            nulos.columns = ["Columna", "% nulos"]
        else:
            nulos = pd.DataFrame({
                "Columna": df.columns,
                "% nulos": 0
            })

        st.dataframe(nulos, use_container_width=True, hide_index=True)

    except pd.errors.EmptyDataError:
        st.error("El dataset está vacío.")


st.divider()
st.subheader("Tabla comparativa de datasets")

comparativa = []
for archivo in directorio.glob("*.csv"):
    
    sep = detectar_separador(archivo) # funcion en src/dataset_utils.py
    df_comp = pd.read_csv(archivo, sep=sep, encoding="utf-8", on_bad_lines='skip')

    pct_coords = cordenadas_validas(df_comp)
    pct_fechas = fechas_validas(df_comp)
    pct_completitud = completitud_promedio(df_comp) 
    
    comparativa.append({
        "Dataset": archivo.name,
        "Registros": len(df_comp),
        "% Coordenadas válidas": pct_coords,
        "% Fechas válidas": pct_fechas,
        "% Completitud promedio": pct_completitud,
    })
    
if comparativa:
    st.dataframe(comparativa, use_container_width=True, hide_index=True)
