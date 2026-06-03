import streamlit as st
import pandas as pd
from src.validacion import verificar_rango
from src.dataset_utils import obtener_columna_real

st.title("🗺️ Ficha de Datos")

# Verifica si hay resultados de busqueda en el estado de sesion
if 'resultados_ficha' not in st.session_state or st.session_state['resultados_ficha'] is None:
    st.warning("No hay resultados de búsqueda. Volvé a la página de Búsqueda.")
    if st.button("← Ir a Búsqueda"):
        st.switch_page("pages/03_Búsqueda.py")
    st.stop()

df = st.session_state['resultados_ficha'].copy()

# Detectar columnas de coordenadas según el dataset
col_lat = obtener_columna_real(df, 'Latitud')
col_lon = obtener_columna_real(df, 'Longitud')

if not col_lat or not col_lon:
    st.error("El dataset no tiene columnas de coordenadas.")
    st.stop()

# Filtrar coordenadas inválidas usando la función del ejercicio 3
def coordenada_valida(row, col_lat, col_lon):
    lat = str(row[col_lat]) if pd.notna(row[col_lat]) else ""
    lon = str(row[col_lon]) if pd.notna(row[col_lon]) else ""
    lat_invalida = verificar_rango(lat, 90, -90)
    lon_invalida = verificar_rango(lon, 180, -180)
    return not lat_invalida and not lon_invalida

# Primero agregar las columnas _lat y _lon a df
df['_lat'] = pd.to_numeric(df[col_lat], errors='coerce')
df['_lon'] = pd.to_numeric(df[col_lon], errors='coerce')

# Después filtrar
mask_validas = df.apply(lambda row: coordenada_valida(row, col_lat, col_lon), axis=1)
df_validos = df[mask_validas].copy()
excluidos = len(df) - len(df_validos)

st.info(f"📍 Mostrando **{len(df_validos)}** registros en el mapa. "
        f"**{excluidos}** fueron excluidos por coordenadas inválidas o nulas.")

if df_validos.empty:
    st.warning("Ningún registro tiene coordenadas válidas para mostrar en el mapa.")
    st.stop()