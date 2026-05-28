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
    'ID': ['id', 'gbifID'],
    'Nombre científico': 'scientificName',
    'Nombre del organismo': 'organismName',
    'Observador': 'recordedBy',
    'Fecha de observación': 'eventDate',
    'Habitat': 'habitat',
    'Continente': 'continent',
    'País': ['country', 'countryCode'],
    'Provincia': 'stateProvince',
    'Latitud': ['decimalLatitude', 'latitudeDecimal'],
    'Longitud': ['decimalLongitude', 'longitudeDecimal'],
    'Reino': 'kingdom',
    'Clase': 'class',
    'Familia': 'family',
    'Género': 'genus',
    'Sexo': 'sex'
}

def obtener_columna_real(df, concepto):
    """
    Busca en el DataFrame cual es el nombre real de la columna 
    basandose en el diccionario de columnas. Retorna el nombre original o None.
    """
    if concepto not in columnas:
        return None
        
    # Creamos un diccionario para mapear la version en minuscula al nombre original
    cols_df_lower = {col.lower(): col for col in df.columns}
    
    # Buscamos cada alias en nuestras columnas
    for alias in columnas[concepto]:
        if alias.lower() in cols_df_lower:
            return cols_df_lower[alias.lower()] # Retornamos el nombre exacto como esta en el CSV
            
    return None # Si no encontro ninguno de los sinónimos

col_pais = obtener_columna_real(df, 'País')
col_latitud = obtener_columna_real(df, 'Latitud')
col_longitud = obtener_columna_real(df, 'Longitud')

# Busqueda libre
st.header("Búsqueda General")
col1, col2 = st.columns([1,2])
with col1:
    col_busqueda = obtener_columna_real(df,st.selectbox("Buscar en la columna:", list(columnas.keys()), index=1))
with col2:
    valor_busqueda = st.text_input("Valor a buscar:", placeholder="Escribe el valor a buscar...")

# Busqueda especifica
st.header("Búsqueda Específica")
filtros_activos = {}

# Funcion auxiliar para obtener valores unicos omitiendo nulos
def valores_unicos(columna):
    if columna in df.columns:
        return sorted(df[columna].dropna().unique().tolist())
    return []

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Columnas para buscar por nombre cientifico, observador, pais y provincia (si existen en el dataset)
with col1:
    if columnas['Nombre científico'] in df.columns:
        sel_cientifico = st.multiselect("Seleccionar Nombre científico:", valores_unicos(columnas['Nombre científico']))
        if sel_cientifico:
            filtros_activos[columnas['Nombre científico']] = sel_cientifico

with col2:
    if columnas['Observador'] in df.columns:
        sel_observador = st.text_input("Seleccionar Observador:", placeholder="Escribe el observador...")
        if sel_observador:
            filtros_activos[columnas['Observador']] = sel_observador

with col3:
    if col_pais:
        sel_pais = st.multiselect("Seleccionar País:", valores_unicos(col_pais))
        if sel_pais:
            filtros_activos[columnas['País']] = sel_pais

with col4:
    if columnas['Provincia'] in df.columns:
        # Si se selecciona un pais, filtrar las provincias disponibles segun ese pais
        opciones_prov = df[df[columnas['País']].isin(sel_pais)][columnas['Provincia']].dropna().unique().tolist() if sel_pais else valores_unicos(columnas['Provincia'])
        sel_provincia = st.multiselect("Seleccionar Provincia o Estado:", opciones_prov)
        if sel_provincia:
            filtros_activos[columnas['Provincia']] = sel_provincia

# Buscar por rango de fechas
if columnas['Fecha de observación'] in df.columns:
    # Intentamos convertir la columna a formato fecha
    fechas_validas = pd.to_datetime(df[columnas['Fecha de observación']], errors='coerce').dropna()
    if not fechas_validas.empty:
        min_fecha = fechas_validas.min()
        max_fecha = fechas_validas.max()
        sel_fecha = st.date_input("Seleccionar rango de fechas:", value=[], min_value=min_fecha, max_value=max_fecha)
        if len(sel_fecha) == 2:
            filtros_activos[columnas['Fecha de observación']] = [pd.to_datetime(sel_fecha[0]), pd.to_datetime(sel_fecha[1])]
    else:
        st.info("El dataset no contiene fechas válidas para filtrar.")
else:
    st.info("La columna de fecha no está disponible en este dataset.")

# Se aplican los filtros
filtro_libre = (col_busqueda, valor_busqueda) if valor_busqueda else None
df_resultados = lec.buscar_registros(df, filtros_activos, filtro_libre)

st.divider()