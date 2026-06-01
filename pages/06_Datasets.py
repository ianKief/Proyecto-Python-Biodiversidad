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

# ruta a directorio de datasets procesados
directorio = Path(__file__).parent.parent / "processed_datasets"

# Recorremos los archivos csv del directorio y obtenemos su nombre, tamaño y fecha de última modificación
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

# Si hay datasets, permitimos seleccionar uno para mostrar su detalle
if datos:
    nombres = [d["Nombre"] for d in datos]
    seleccionado = st.selectbox("Seleccioná un dataset para ver su detalle", nombres)

    try:
        sep = detectar_separador(directorio / seleccionado)
        df = pd.read_csv(directorio / seleccionado, sep=sep, encoding="utf-8", on_bad_lines="skip")

        # Mostramos métricas básicas como cantidad de registros y columnas
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
# Recorremos los datasets para calcular métricas comparativas. Nombre, cantidad de registros, porcentaje de coordenadas válidas, fechas válidas y completitud promedio
for archivo in directorio.glob("*.csv"):    
    sep = detectar_separador(archivo) 
    df_comp = pd.read_csv(archivo, sep=sep, encoding="utf-8", on_bad_lines='skip')
    
    comparativa.append({
        "Dataset": archivo.name,
        "Registros": len(df_comp),
        "% Coordenadas válidas": cordenadas_validas(df_comp),
        "% Fechas válidas": fechas_validas(df_comp),
        "% Completitud promedio": completitud_promedio(df_comp),
    })
    
if comparativa:
    st.dataframe(comparativa, use_container_width=True, hide_index=True)
 

st.divider()
st.subheader("Documentación")

# Mostramos una lista de documentos disponibles en documentation/ para que el usuario pueda seleccionar uno y ver su contenido
dir_docs = Path(__file__).parent.parent / "documentation"
docs = [f.name for f in dir_docs.glob("*.md")]

if docs:
    doc_seleccionado = st.selectbox("Seleccioná un documento", docs) 
    with open(dir_docs / doc_seleccionado, encoding="utf-8") as f:
        contenido = f.read()
    st.markdown(contenido)
else:
    st.warning("No hay documentos disponibles en documentation/")
