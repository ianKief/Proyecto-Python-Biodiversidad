import streamlit as st
import pandas as pd
import os


st.set_page_config(
    page_title="Gestión de Registros",
    page_icon="🗂️"
)

st.title("Gestión de Registros")

rute=os.path.join("processed_datasets", f"{st.session_state['archivo']}")
if not rute or not os.path.exists(rute):
    st.warning("No se encontró el dataset procesado. Por favor, selecciona un dataset válido en la barra lateral.")
    st.stop()

if not(os.access(rute, os.W_OK)):
    st.error("No se tienen permisos de escritura en el archivo. No se pueden eliminar registros.")
    st.stop()
    
df=pd.read_csv(rute)

if (df.empty):
    st.warning("El dataset está vacío. No se pueden generar visualizaciones.")
    st.stop()

#Ejercicio 4.B

ejemplo_id={
    "iadiza_procesado.csv":["1660909562", "gbifID"],
    "inaturalist_procesado.csv":["56389512", "id"],
    "xeno-canto_procesado.csv":["572960@XC o 3954627@XC", "id"]
}

st.subheader("Buscar un registro por ID")
registro_id=st.text_input(f"Ingrese el ID que desea buscar (ejemplo: {ejemplo_id.get(st.session_state['archivo'])[0]})", key="registro_a_eliminar")

try:
    if st.button("Buscar Registro"):
        id_columna=ejemplo_id.get(st.session_state['archivo'])[1]
        registro_encontrado=df[df[id_columna].astype(str)==registro_id]
        if not registro_encontrado.empty:
            st.success("Registro encontrado:")
            st.data_editor(registro_encontrado)
        else:
            st.warning("No se encontró ningún registro con ese ID.")
except Exception as e:
    st.error(f"Ocurrió un error al buscar el registro: {e}")