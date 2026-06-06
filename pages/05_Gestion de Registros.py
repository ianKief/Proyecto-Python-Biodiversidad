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

registro={}


ejemplo_id={
    "iadiza_procesado.csv":["1660909562", "gbifID"],
    "inaturalist_procesado.csv":["56389512", "id"],
    "xeno-canto_procesado.csv":["572960@XC o 3954627@XC", "id"]
}

#Ejercicio 4.A

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

st.subheader("Ingresar registro al dataset")
st.write("Ingrese los datos del nuevo registro")

campos_dataset=[]

for col in columnas:
    if len(columnas[col])>1:
        if columnas[col][0] in df.columns:
            campos_dataset.append(columnas[col][0])
        elif columnas[col][1] in df.columns:
            campos_dataset.append(columnas[col][1])
    else:
        if columnas[col][0] in df.columns:
            campos_dataset.append(columnas[col][0])

nuevo_registro=st.data_editor(pd.DataFrame(index=[0],columns=campos_dataset), key="nuevo_registro")
if st.button("Validar datos e insertar"):
    nuevo=dict(nuevo_registro.iloc[0])
    nuevo={campo: (None if pd.isna(valor) else valor) for campo, valor in nuevo.items()} #Convierto los pd.Na a None para que la validacion funcione correctamente
    st.write(nuevo)
    es_valido, errores = validar_registro(nuevo)

    #Validaciones no hechas en la función validar_registro

    #Validar ID
    if st.session_state['dataset'] == "xeno-canto":
        campo_id=ejemplo_id.get(st.session_state['archivo'])[1]
        if not no_existe_dato(nuevo[campo_id]):
            if not str(nuevo[campo_id]).endswith("@XC"):
                errores.append("El ID debe terminar con @XC")
            else:
                id_sin_xc = str(nuevo["id"]).replace("@XC", "")
                if not id_sin_xc.isdigit():
                    errores.append("La parte numérica del ID debe ser un número entero")
    else:
            campo_id=ejemplo_id.get(st.session_state['archivo'])[1]
            if not no_existe_dato(nuevo[campo_id]):
                if not str(nuevo[campo_id]).isdigit():
                    errores.append("El ID debe ser un número entero")
            else:
                errores.append("El campo ID no puede estar vacío")

    #Validacion fecha
    if pd.to_datetime(nuevo.get("eventDate"), errors='coerce') is pd.NaT:
        errores.append("El valor de eventDate no es una fecha válida")

    #Validar valor en caso de tener el nombre del pais y no su codigo
    if "country" in nuevo:
        if not no_existe_dato(nuevo["country"]):
        #Como pycountry tiene los nombres de los paises en ingles, se hace una traduccion previa para validar el nombre del pais en español
            idioma=Locale("es")
            paises={}
            for pais in pycountry.countries:
                try:
                    nombre_es = idioma.territories[pais.alpha_2].lower()
                    paises[nombre_es] = pais
                except KeyError:
                    pass
        
            if nuevo["country"].lower() not in paises.keys():
                errores.append("El nombre del país no es reconocido")
        else:
            errores.append("El campo country no puede estar vacio")

    #Validar continente
    continentes=["Africa", "Antarctida", "Asia", "Europa", "America", "Oceania"]
    if "continent" in nuevo:
        if not no_existe_dato(nuevo["continent"]):
            if nuevo["continent"].strip().capitalize() not in continentes:
                errores.append("El nombre del continente no es reconocido")
        else:
            errores.append("El campo continent no puede estar vacío")

    #Validar campos de strings
    campos_strings=["scientificName", "organismName", "recordedBy", "habitat", "stateProvince", "kingdom", "class", "family", "genus", "sex"]
    for campo in campos_strings:
        if campo in nuevo:
            if not no_existe_dato(nuevo[campo]):
                if not isinstance(nuevo[campo], str):
                    errores.append(f"El campo {campo} debe ser una cadena de texto")
                
                    if any(caracter.isdigit() for caracter in nuevo[campo]):
                        errores.append(f"El campo {campo} no puede contener números")

                    if len(nuevo[campo])==1:
                        errores.append(f"El campo {campo} no puede contener una sola letra")
            else:
                errores.append(f"El campo {campo} no puede estar vacío")
                

    if errores:
        st.warning("El registro tiene los siguientes errores:")
        for error in errores:
            st.write(f"- {error}")
    else:
        st.success("El registro es válido y se puede insertar en el dataset.")
        try:
            #Reutilizo la logica de insercion
            with open(rute, "a", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f,fieldnames=df.columns, delimiter=",")
                writer.writerow(nuevo)
            st.success("El registro fue insertado sin problemas")
        except Exception as e:
                st.write(f"Hubo un error: {e}")


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