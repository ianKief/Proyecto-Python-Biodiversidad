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
    st.error("No se pudo cargar el dataset o el mismo esta vacío. Por favor, verifica tu selección.")
    st.stop()

st.title("🔍 Búsqueda Avanzada")

# Columnas de prueba
columnas = {
    'ID': ['id', 'gbifID'],
    'Nombre científico': ['scientificName'],
    'Nombre del organismo': ['organismName'],
    'Observador': ['recordedBy'],
    'Fecha de observación': ['eventDate'],
    'Habitat': ['habitat'],
    'Continente': ['continent'],
    'País': ['country', 'countryCode'],
    'Provincia': ['stateProvince'],
    'Latitud': ['decimalLatitude', 'latitudeDecimal'],
    'Longitud': ['decimalLongitude', 'longitudeDecimal'],
    'Reino': ['kingdom'],
    'Clase': ['class'],
    'Familia': ['family'],
    'Género': ['genus'],
    'Sexo': ['sex']
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

col_id = obtener_columna_real(df, 'ID')
col_nombre_cientifico = obtener_columna_real(df, 'Nombre científico')
col_nombre_organismo = obtener_columna_real(df, 'Nombre del organismo')
col_observador = obtener_columna_real(df, 'Observador')
col_fecha_observacion = obtener_columna_real(df, 'Fecha de observación')
col_habitat = obtener_columna_real(df, 'Habitat')
col_continente = obtener_columna_real(df, 'Continente')
col_pais = obtener_columna_real(df, 'País')
col_provincia = obtener_columna_real(df, 'Provincia')
col_latitud = obtener_columna_real(df, 'Latitud')
col_longitud = obtener_columna_real(df, 'Longitud')
col_reino = obtener_columna_real(df, 'Reino')
col_clase = obtener_columna_real(df, 'Clase')
col_familia = obtener_columna_real(df, 'Familia')
col_genero = obtener_columna_real(df, 'Género')
col_sexo = obtener_columna_real(df, 'Sexo')

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
    if columna and columna in df.columns:
        return sorted(df[columna].astype(str).str.strip().dropna().unique().tolist())
    return []

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Columnas para buscar por nombre cientifico, observador, pais y provincia (si existen en el dataset)
with col1:
    if col_nombre_cientifico in df.columns:
        sel_cientifico = st.multiselect("Seleccionar Nombre científico:", valores_unicos(col_nombre_cientifico))
        if sel_cientifico:
            filtros_activos[col_nombre_cientifico] = sel_cientifico

with col2:
    if col_observador in df.columns:
        sel_observador = st.text_input("Seleccionar Observador:", placeholder="Escribe el observador...")
        if sel_observador:
            filtros_activos[col_observador] = sel_observador

with col3:
    if col_pais:
        sel_pais = st.multiselect("Seleccionar País:", valores_unicos(col_pais))
        if sel_pais:
            filtros_activos[col_pais] = sel_pais

with col4:
    if col_provincia in df.columns:
        # Si se selecciona un pais, filtrar las provincias disponibles segun ese pais
        opciones_prov = df[df[col_pais].isin(sel_pais)][col_provincia].dropna().unique().tolist() if sel_pais else valores_unicos(col_provincia)
        sel_provincia = st.multiselect("Seleccionar Provincia o Estado:", opciones_prov)
        if sel_provincia:
            filtros_activos[col_provincia] = sel_provincia

# Buscar por rango de fechas
if col_fecha_observacion in df.columns:
    # Intentamos convertir la columna a formato fecha
    fechas_validas = pd.to_datetime(df[col_fecha_observacion], errors='coerce').dropna()
    if not fechas_validas.empty:
        min_fecha = fechas_validas.min()
        max_fecha = fechas_validas.max()
        sel_fecha = st.date_input("Seleccionar rango de fechas:", value=[], min_value=min_fecha, max_value=max_fecha)
        if len(sel_fecha) == 2:
            filtros_activos[col_fecha_observacion] = [pd.to_datetime(sel_fecha[0]), pd.to_datetime(sel_fecha[1])]
    else:
        st.info("El dataset no contiene fechas válidas para filtrar.")
else:
    st.info("La columna de fecha no está disponible en este dataset.")

# Se aplican los filtros
filtro_libre = (col_busqueda, valor_busqueda) if valor_busqueda else None
df_resultados = lec.buscar_registros(df, filtros_activos, filtro_libre)

st.divider()

# Muestra de resultados
st.subheader("Resultados de la búsqueda")
if df_resultados.empty:
    st.warning("No se encontraron resultados que coincidan con los criterios de búsqueda.")
else:
    # Defino las columnas a mostrar en el resultado, solo las que existan en el dataset
    columnas_relevantes = [col_id,
                           col_nombre_cientifico,
                           col_nombre_organismo,
                           col_observador,
                           col_fecha_observacion,
                           col_habitat,
                           col_continente,
                           col_pais,
                           col_provincia,
                           col_latitud,
                           col_longitud,
                           col_reino,
                           col_clase,
                           col_familia,
                           col_genero,
                           col_sexo]
    # En la tabla de resultados solo se muestran las columnas que existen en el dataset
    columnas_finales = [col for col in columnas_relevantes if col is not None]

    dict_renombres = {}
    if col_id: dict_renombres[col_id] = "ID"
    if col_nombre_cientifico: dict_renombres[col_nombre_cientifico] = "Nombre Científico"
    if col_nombre_organismo: dict_renombres[col_nombre_organismo] = "Nombre del Organismo"
    if col_observador: dict_renombres[col_observador] = "Observador"
    if col_fecha_observacion: dict_renombres[col_fecha_observacion] = "Fecha"
    if col_habitat: dict_renombres[col_habitat] = "Habitat"
    if col_continente: dict_renombres[col_continente] = "Continente"
    if col_pais: dict_renombres[col_pais] = "País"
    if col_provincia: dict_renombres[col_provincia] = "Provincia"
    if col_latitud: dict_renombres[col_latitud] = "Latitud"
    if col_longitud: dict_renombres[col_longitud] = "Longitud"
    if col_reino: dict_renombres[col_reino] = "Reino"
    if col_clase: dict_renombres[col_clase] = "Clase"
    if col_familia: dict_renombres[col_familia] = "Familia"
    if col_genero: dict_renombres[col_genero] = "Género"
    if col_sexo: dict_renombres[col_sexo] = "Sexo"

    df_vista = df_resultados.head(20)[columnas_finales].rename(columns=dict_renombres)

    st.dataframe(df_vista, use_container_width=True, hide_index=True)

    # Acceso al detalle de un registro
    st.markdown("### Detalle de un registro")
    if col_id:
        id_detalle = st.selectbox("Seleccionar ID para ver detalle:", df_resultados[col_id].dropna().unique())
        if id_detalle:
            registro_detalle = df_resultados[df_resultados[col_id] == id_detalle].iloc[0]
            st.write(registro_detalle.to_frame().T)  # Muestra el registro completo en formato tabla
    else:
        st.caption("No se puede mostrar el detalle de un registro porque no se encontró una columna de ID en el dataset.")