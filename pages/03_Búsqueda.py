import streamlit as st
import pandas as pd
import src.lectura as lec
from datetime import datetime

@st.cache_data(show_spinner="Cargando dataset...")
def cargar_dataset_cache(dataset):
    """
    Carga el dataset en caché para que no tenga que volver a cargarlo cada vez que se actualice la página
    """
    df = lec.obtener_dataset(dataset)
    if df is not None:
        return df
    return pd.DataFrame()  # Retorna un DataFrame vacío si no se pudo cargar el dataset

dataset = st.session_state.get('dataset_seleccionado', None)

if not dataset:
    st.warning("No se ha seleccionado ningún dataset. Por favor, selecciona un dataset en la página de selección.")
    st.stop()

df = cargar_dataset_cache(dataset)

if df.empty:
    st.error("No se pudo cargar el dataset. Por favor, verifica tu selección.")
    st.stop()

st.title("🔍 Búsqueda Avanzada")

# Columnas de prueba
columnas = {
    'ID': 'id',
    'Nombre científico': 'scientificName',
    'Nombre del organismo': 'organismName',
    'Observador': 'recordedBy',
    'Fecha de observación': 'eventDate',
    'Habitat': 'habitat',
    'Continente': 'continent',
    'País': 'country',
    'Provincia': 'stateProvince',
    #latitud y longitud
    'Reino': 'kingdom',
    'Clase': 'class',
    'Familia': 'familiy',
    'Género': 'genus'
}

# Busqueda libre
st.header("Búsqueda General")
col1, col2 = st.columns([1,2])
with col1:
    col_busqueda = st.selectbox("Buscar en la columna:", list(columnas.keys()), index=1)
with col2:
    valor_busqueda = st.text_input("Valor a buscar:", placeholder="Escribe el valor a buscar...")