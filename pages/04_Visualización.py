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
eleccion=st.selectbox("Selecciona como quiere que sea la distribucion", ("Pais","Provincia"))

if eleccion=="Pais":
    campo=[datos for datos in df.columns if "country" in datos.lower()][0]
elif eleccion=="Provincia":
    if "stateProvince" in df.columns:
        campo="stateProvince"
    else:
        campo="locality"

try:
    total=df[campo].value_counts()
    if total.empty:
        st.warning(f"No se encontraron datos para la columna {campo}.")

    if len(total)>1:
        if campo=="countryCode":
            indices=total.index.map(lambda x: pc.countries.get(alpha_2=x).name if pc.countries.get(alpha_2=x) else None)
            total = total[indices.notna()]
            total.index = indices[indices.notna()]
        elif campo=="country":
            indices=total.index.map(lambda x: pc.countries.get(name=x).name if pc.countries.get(name=x) else None)
            total = total[indices.notna()]
            total.index = indices[indices.notna()]

        cantidad=st.slider("Cantidad de datos a mostrar", min_value=1, max_value=total.shape[0], value=3)
        datos=total.head(cantidad)
    
        plt.figure(figsize=(10, 5))
        plt.bar(datos.index, datos.values)
        plt.xticks(rotation=90)
        plt.title(f"Distribución de registros por {eleccion}")
        plt.xlabel(eleccion)
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

    if validas.empty:
        st.warning("No se encontraron fechas válidas en la columna 'eventDate'. No se puede generar la gráfica de registros por año.")
    else:
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
    if total.empty:
        st.warning(f"No se encontraron datos para la columna {columnas[opcion]}.")
    else:
        if total.shape[0]==1:
            cant=total.values[0]
            st.write("Solo hay un valor en la columna seleccionada, por lo que se mostrará la distribución de ese único valor.")
        else:
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
else:
    
    eleccion=st.slider("Cantidad de columnas a mostrar", min_value=1, max_value=len(nulos["Promedio nulos por columna"]), value=3,      key="slider_nulos")
    nulos=100-pd.Series(nulos["Promedio nulos por columna"]).head(eleccion)


    try:
        plt.figure(figsize=(10, 5))
        plt.barh(nulos.index, nulos.values)
        plt.xticks(rotation=90)
        plt.title("Porcentaje de registros no nulos por columna")
        plt.xlabel("Porcentaje de registros no nulos")
        plt.ylabel("Columnas")
        st.pyplot(plt)
    except Exception as e:
        st.error(f"No se pudo generar la gráfica de porcentaje de registros no nulos. Asegúrate de que el análisis de nulos se haya realizado correctamente. Error: {e}")


#Ejercicio 3.E
ruta_carpeta=os.path.join("processed_datasets")

cant=len(os.listdir(ruta_carpeta))

informacion={
    "Dataset": [],
    "Cantidad de registros": [],
    "Porcentaje de coordenadas válidas": [],
    "Porcentaje de fechas válidas": [],
    "Completitud promedio": []
}

st.subheader("Comparación entre datasets")
if cant>1:
    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".csv"):
            df_temp=pd.read_csv(os.path.join(ruta_carpeta, archivo))

            if df_temp.empty:
                st.warning(f"El dataset {archivo} está vacío. No se pueden calcular las métricas para este dataset.")
                continue

            cantidad=df_temp.shape[0]
            coord_validas=du.cordenadas_validas(df_temp)
            fechas_validas=du.fechas_validas(df_temp)
            completitud=du.completo(df_temp)
            informacion["Dataset"].append(archivo)
            informacion["Cantidad de registros"].append(cantidad)
            informacion["Porcentaje de coordenadas válidas"].append(coord_validas)
            informacion["Porcentaje de fechas válidas"].append(fechas_validas)
            informacion["Completitud promedio"].append(completitud)
    
    tabla=pd.DataFrame(informacion)
    st.table(tabla)
else:
    st.warning("No hay suficientes datasets procesados para comparar. Por favor, procesa más datasets para ver la comparación.")

