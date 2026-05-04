import streamlit as st
import csv
import os

st.set_page_config(
    page_title="Estado del Sistema",
    page_icon="📊" 
)

st.title("Estado del Sistema")
st.write("Registro de operaciones realizadas en el sistema.")

# Ruta del archivo
log_path = os.path.join("logs", "operations.log")

if os.path.exists(log_path):
    try:
        logs = []
        with open(log_path, "r", encoding="utf-8") as archivo_log:
            for linea in archivo_log:
                partes = [parte.strip() for parte in linea.split("|")] # Separo por el delimitador y limpio espacios
                if partes:
                    # logs tendra una lista de diccionarios con las partes del log
                    logs.append({
                        "Fecha": partes[0],
                        "Dataset": partes[1],
                        "Operation": partes[2],
                        "Registros": partes[3],
                    })
        if logs:
            st.dataframe(logs, use_container_width=True, hide_index=True)
            st.success(f"Se cargaron {len(logs)} registros de operaciones.")
        else:
            st.warning("No se encontraron registros de operaciones.")
    except Exception as e:
        st.error(f"Error al leer el archivo de log: {e}")
else:
    st.warning("El archivo de log no existe.")
    st.caption(f"Buscando en: {log_path}")