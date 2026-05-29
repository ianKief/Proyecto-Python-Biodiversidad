import streamlit as st
import src.lectura as lec
import datetime


# Selección del dataset. Se usa session_state para que la elección se mantenga persistente entre paginas
if 'dataset' not in st.session_state:
    st.session_state['dataset'] = None
if 'fecha_hora' not in st.session_state:
    st.session_state['fecha_hora'] = None
if 'archivo' not in st.session_state:
    st.session_state['archivo'] = None

def actualizar_seleccion():
    st.session_state['dataset'] = st.session_state['dataset_seleccionado']
    st.session_state['fecha_hora'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.session_state['archivo'] = st.session_state['dataset'] + "_procesado.csv"

with st.sidebar.expander("Información del dataset seleccionado"):
    st.title("⚙️ Configuración")
    opciones = ["iadiza", "inaturalist", "xeno-canto"]
    index_actual = opciones.index(st.session_state['dataset']) if st.session_state['dataset'] in opciones else 0
    st.selectbox("Selecciona un dataset", 
                         opciones, 
                         key='dataset_seleccionado', 
                         index=index_actual,
                     on_change=actualizar_seleccion)
    st.write("---")
    st.info(f"📁 Dataset activo: **{st.session_state['dataset']}**")
    
    # Manejo seguro por si falla la lectura del CSV al arrancar
    try:
        cant = lec.cant_registros(st.session_state['dataset'], st.session_state['archivo'])
        st.success(f"📊 Registros: **{cant}**")
    except Exception:
        st.warning("📊 Registros: No calculados")
        
    st.caption(f"🕒 Última selección:\n{st.session_state['fecha_hora']}")

# Configuracion de navegacion entre paginas
pagina_inicio = st.Page("pages/01_Inicio.py", title="Inicio", icon="🏠", default=True)
pagina_estado = st.Page("pages/02_Estado del Sistema.py", title="Estado", icon="⚙️")
pagina_busqueda = st.Page("pages/03_Búsqueda.py", title="Búsqueda", icon="🔍")
pagina_visualizacion = st.Page("pages/04_Visualización.py", title="Visualización", icon="📊")
pagina_gestion = st.Page("pages/05_Gestion de Registros.py", title="Gestión", icon="🗂️")
pagina_datasets = st.Page("pages/06_Datasets.py", title="Datasets", icon="📁")

pg = st.navigation([pagina_inicio, pagina_estado, pagina_busqueda, pagina_visualizacion, pagina_gestion, pagina_datasets])
pg.run()