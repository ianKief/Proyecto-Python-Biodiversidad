import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
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

# Selector de criterio de color
col_cientifico = obtener_columna_real(df, 'Nombre científico')
col_pais = obtener_columna_real(df, 'País')
col_familia = obtener_columna_real(df, 'Familia')

opciones_color = {}
if col_pais: opciones_color['País'] = col_pais
if col_cientifico: opciones_color['Especie'] = col_cientifico
if col_familia: opciones_color['Familia'] = col_familia

criterio_label = st.selectbox("🎨 Colorear puntos por:", list(opciones_color.keys()))
criterio_col = opciones_color[criterio_label]

# Generar colores por categoría
categorias = df_validos[criterio_col].fillna('Sin datos').astype(str).unique()
paleta = [
    '#e6194b','#3cb44b','#ffe119','#4363d8','#f58231',
    '#911eb4','#42d4f4','#f032e6','#bfef45','#fabebe',
    '#469990','#dcbeff','#9A6324','#fffac8','#800000',
    '#aaffc3','#808000','#ffd8b1','#000075','#a9a9a9'
]
color_map = {cat: paleta[i % len(paleta)] for i, cat in enumerate(categorias)}

# Crear mapa centrado en el promedio de coordenadas
lat_centro = df_validos['_lat'].mean()
lon_centro = df_validos['_lon'].mean()

mapa = folium.Map(location=[lat_centro, lon_centro], zoom_start=4)
cluster = MarkerCluster(options={
        'spiderfyOnMaxZoom': True,
        'spiderfyDistanceMultiplier': 2,
        'zoomToBoundsOnClick': True,
    }
).add_to(mapa)

# Detectar columna ID
col_id = obtener_columna_real(df, 'ID')

for _, row in df_validos.iterrows():
    categoria = str(row[criterio_col]) if criterio_col in row and pd.notna(row[criterio_col]) else 'Sin datos'
    color = color_map.get(categoria, '#808080')
    
    id_val = str(row[col_id]) if col_id else '—'
    nombre = str(row[col_cientifico]) if col_cientifico else '—'
    
    popup_html = f"""
        <b>ID:</b> {id_val}<br>
        <b>Especie:</b> {nombre}<br>
        <b>{criterio_label}:</b> {categoria}
    """
    
    folium.CircleMarker(
        location=[row['_lat'], row['_lon']],
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=nombre
    ).add_to(cluster)

st.markdown("#### Mapa de ocurrencias")
resultado_mapa = st_folium(mapa, width=900, height=500)
