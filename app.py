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

opciones = ["iadiza", "inaturalist", "xeno-canto"]
st.sidebar.selectbox("Selecciona un dataset", 
                     opciones, 
                     key='dataset_seleccionado', 
                     on_change=actualizar_seleccion)

st.sidebar.info(f"Dataset seleccionado: **{st.session_state['dataset']}**")
st.sidebar.info(f"Cantidad de registros: **{lec.cant_registros(st.session_state['dataset'], st.session_state['archivo'])}**")
st.sidebar.info(f"Fecha y Hora de selección: **{st.session_state['fecha_hora']}**")
st.sidebar.info(f"Archivo procesado: **{st.session_state['archivo']}**")