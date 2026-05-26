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

st.subheader("Cantidad de registros por año")
st.write(f"Aca se muestra un grafico de la cantidad de registros por año del dataset: {st.session_state['dataset']}")

try:
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
except:
    st.error("No se pudo generar la gráfica de registros por año. Asegúrate de que la columna 'eventDate' exista")

st.subheader("Distribución por clase, orden o familia")
st.write(f"Aca se muestra un grafico de la distribucion de registros por clase, orden o familia del dataset: {st.session_state['dataset']}")

opcion=st.selectbox("Selecciona una columna para visualizar su distribución", ("class","order","family"))

try:
    total=df[opcion].value_counts()
    cant=st.slider("Cantidad de datos a mostrar", min_value=1, max_value=total.shape[0], value=1)
    datos=total.head(cant)

    plt.figure(figsize=(10, 5))
    plt.pie(datos.values,labels=datos.index,autopct="%1.1f%%")
    plt.title(f"Distribución de registros por {opcion}")
    st.pyplot(plt)
    
except Exception as e:
    st.error(f"La columna {opcion} no existe en el dataset")