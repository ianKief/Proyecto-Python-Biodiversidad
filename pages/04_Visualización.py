import streamlit as st
import os
import matplotlib.pyplot as plt
import pandas as pd


st.set_page_config(
    page_title="Visualización",
    page_icon="📊"
)

st.title("Visualización de Datos")

st.write(f"Aca se muestra un grafico de la cantidad de registros por año del dataset: {st.session_state['dataset']}")

rute=os.path.join("processed_datasets", f"{st.session_state['dataset']}_procesado.csv")
if not rute or not os.path.exists(rute):
    st.warning("No se encontró el dataset procesado. Por favor, selecciona un dataset válido en la barra lateral.")
    st.stop()

df=pd.read_csv(rute)

if (df.empty):
    st.warning("El dataset está vacío. No se pueden generar visualizaciones.")
    st.stop()

fechas=pd.to_datetime(
    df['eventDate'],
    errors="coerce"
)

excluidos=fechas.isna().sum()

validas=fechas.dropna()
años=validas.dt.year.value_counts().sort_index()

plt.figure(figsize=(10,5))
plt.plot(años.index, años.values, marker='o')

plt.title("cantidad de registros por año")

plt.xlabel("Año")
plt.ylabel("Cantidad de registros")
plt.grid(True)
st.pyplot(plt)

st.write(f"Se excluyeron {excluidos} registros por tener fechas no válidas o vacías.")