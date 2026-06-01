import streamlit as st
import os
import matplotlib.pyplot as plt
import pandas as pd
import pycountry as pc
from src.lectura import analisis_nulos


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

if not(os.access(rute, os.R_OK)):
    st.error("No se tiene permiso para leer el archivo del dataset. Por favor, verifica los permisos del archivo.")
    st.stop()

df=pd.read_csv(rute)

if (df.empty):
    st.warning("El dataset está vacío. No se pueden generar visualizaciones.")
    st.stop()

#Ejercicio 3.A
st.subheader("Distribución de registros por país o por provincia")
st.write(f"Aca se muestra un grafico de la distribucion de registros por país o por provincia del dataset: {st.session_state['dataset']}")
eleccion=st.selectbox("Selecciona como quiere que sea la distribucion", ("pais","provincia"))

if eleccion=="pais":
    campo=[datos for datos in df.columns if "country" in datos.lower()][0]
elif eleccion=="provincia":
    if "stateProvince" in df.columns:
        campo="stateProvince"
    else:
        campo="locality"

try:
    total=df[campo].value_counts()
    if total.empty:
        st.warning(f"No se encontraron datos para la columna {campo}.")

    if len(total)>1:
        cantidad=st.slider("Cantidad de datos a mostrar", min_value=1, max_value=total.shape[0], value=3)
        datos=total.head(cantidad)
    
        if eleccion=="pais":
            if campo=="countryCode":
                datos.index=datos.index.map(lambda x: pc.countries.get(alpha_2=x).name if pc.countries.get(alpha_2=x) else x)
            plt.figure(figsize=(10, 5))
            plt.bar(datos.index, datos.values)
            plt.xticks(rotation=90)
            plt.title("Distribución de registros por país")
            plt.xlabel("País")
            plt.ylabel("Cantidad de registros")
            st.pyplot(plt)
        else:
            plt.figure(figsize=(10, 5))
            plt.bar(datos.index, datos.values)
            plt.xticks(rotation=90)
            plt.title("Distribución de registros por provincia")
            plt.xlabel("Provincia")
            plt.ylabel("Cantidad de registros")
            st.pyplot(plt)
    else:
        st.warning(f"No se puede hacer la distribucion por {eleccion} porque todos los registros son del mismo lugar: {total.index[0]}.")

except Exception as e:
    st.error(f"No se pudo generar la gráfica de distribución por {eleccion}. Asegúrate de que la columna correspondiente exista en el dataset. Error: {e}")

#Ejercicio 3.B
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


#Ejercicio 3.C
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

#Ejercicio 3.D
st.subheader("porcentaje de registros no nulos por columna")
st.write(f"Aca se muestra un grafico del porcentaje de registros no nulos por columna del dataset: {st.session_state['dataset']}")

nulos=analisis_nulos(st.session_state['dataset'], st.session_state['archivo'])

if not nulos:
    st.warning("No se pudo realizar el análisis de nulos. Asegúrate de que el dataset esté correctamente procesado.")
    st.stop()
    
eleccion=st.slider("Cantidad de columnas a mostrar", min_value=1, max_value=len(nulos["Promedio nulos por columna"]), value=3,key="slider_nulos")
nulos=pd.Series(nulos["Promedio nulos por columna"]).head(eleccion)


try:
    plt.figure(figsize=(10, 5))
    plt.barh(nulos.index, nulos.values*100)  # Multiplicar por 100 para obtener porcentajes
    plt.xticks(rotation=90)
    plt.title("Porcentaje de registros no nulos por columna")
    plt.xlabel("Columna")
    plt.ylabel("Porcentaje de registros no nulos")
    st.pyplot(plt)
except Exception as e:
    st.error(f"No se pudo generar la gráfica de porcentaje de registros no nulos. Asegúrate de que el análisis de nulos se haya realizado correctamente. Error: {e}")