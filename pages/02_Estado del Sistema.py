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
            filtro = st.selectbox("Elija como quiere filtar los logs",["Sin filtro","Por fecha","Por operacion","Resumen"]              key="filtro_logs")

            if filtro == "Por operacion":
                operacion_filtro = st.selectbox("Seleccione la operación a filtrar", ["INSERT", "UPDATE", "DELETE", "ERROR"], key="operacion_filtro")

            elif filtro == "Por fecha":
                fecha_min=st.date_input("Fecha mínima", key="fecha_min")
                fecha_max=st.date_input("Fecha máxima", key="fecha_max")
                if fecha_min > fecha_max:
                    st.warning("La fecha mínima no puede ser mayor que la fecha máxima.")

            for linea in archivo_log:
                partes = [parte.strip() for parte in linea.split("|")] # Separo por el delimitador y limpio espacios
                if partes:
                    if filtro == "Por operacion":
                        if not (partes[2] == operacion_filtro):
                            continue
                    elif filtro == "Por fecha":
                        fecha=datetime.strptime(partes[0].split(" ")[0], "%Y-%m-%d") # Extraigo solo la parte de la fecha
                        if not (fecha_min <= fecha.date() <= fecha_max):
                            continue
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

            if filtro =="Resumen":
                resumen = {}
                for log in logs:
                    op = log["Operation"]
                    resumen[op] = resumen.get(op, 0) + 1
                st.subheader("Resumen de Operaciones")
                st.table(resumen.items())
        else:
            st.warning("No se encontraron registros de operaciones.")
    except Exception as e:
        st.error(f"Error al leer el archivo de log: {e}")
else:
    st.warning("El archivo de log no existe.")
    st.caption(f"Buscando en: {log_path}")