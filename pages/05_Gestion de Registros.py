import streamlit as st
import pandas as pd
import os
import csv
import pycountry
import src.eliminacion as eli
import time
from dateutil import parser
from src.insercion import validar_registro
from babel import Locale
from src.actualizacion import actualizar_multiples_campos
from src.validacion import no_existe_dato


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

st.info("Recordá presionar ENTER después de ingresar un dato en una celda")
nuevo_registro=st.data_editor(pd.DataFrame(index=[0],columns=campos_dataset), key="nuevo_registro")
if st.button("Validar datos e insertar"):
    print(nuevo_registro)
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
        errores.append("El valor de eventDate no es una fecha válida. El formato esperado es ISO 8601 (Ej: 2023-08-15T14:30:00Z)")

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
    continentes=["Africa", "Antartida", "Asia", "Europa", "America", "Oceania"]
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
            time.sleep(2)
            st.rerun()
        except Exception as e:
                st.write(f"Hubo un error: {e}")

st.divider()

#Ejercicio 4.B

st.subheader("Buscar un registro por ID")
registro_id=st.text_input(f"Ingrese el ID que desea buscar (ejemplo: {ejemplo_id.get(st.session_state['archivo'])[0]})", key="registro_a_buscar")

if st.button("Buscar Registro"):
    try:
        id_columna=ejemplo_id.get(st.session_state['archivo'])[1]
        registro_encontrado=df[df[id_columna].astype(str)==registro_id]
        if registro_encontrado.empty:
            st.warning("No se encontró ningún registro con ese ID.")
            if "registro_encontrado" in st.session_state:
                del st.session_state["registro_encontrado"]
        else:
            st.session_state["registro_encontrado"]=registro_encontrado
            st.success("Registro encontrado. Edite los campos a continuación:")

    except Exception as e:
        st.error(f"Ocurrió un error al buscar el registro: {e}")

#Ejercicio 4.C
st.subheader("Actualizar registro encontrado")
st.write("Una vez relizada la busqueda del registro aca podra modificar los campos deseados")

if "registro_encontrado" in st.session_state:
    st.info("Recordá presionar ENTER después de ingresar un dato en una celda")
    original=dict(st.session_state["registro_encontrado"].iloc[0])
    editado=st.data_editor(st.session_state["registro_encontrado"],key="editor")


    if st.button("Validar registro encontrado y modificarlo"):
        print(f"Registro editado: {editado}")
        editado_dict=dict(editado.iloc[0])
        cambios={}

        for campo in original:
            val_original=original[campo]
            val_editado=editado_dict[campo]
            if pd.isna(val_original) and pd.isna(val_editado):
                continue

            if val_editado!=val_original:
                cambios[campo]=val_editado
                
        if not cambios:
            st.warning("No se detectaron modificaciones")
        else:
            try:
                columna_ID=ejemplo_id[st.session_state['archivo']][1]
                actualizar=actualizar_multiples_campos(st.session_state['dataset'],
                                                        st.session_state['archivo'],
                                                        columna_ID,
                                                        str(original[columna_ID]),
                                                        cambios)
                if actualizar == "Columnas actualizadas exitosamente":
                    st.success("Registro actualizado exitosamente")
                    del st.session_state["registro_encontrado"]
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"No se pudo actualizar el registro: {actualizar}")
            except Exception as e:
                st.error(f"Hubo un error a la hora de actualizar el registro, {e}")

st.divider()

#Ejercicio 4.D
st.subheader("Eliminar un registro")
opcion_eliminar=st.radio(label="Seleccione el método de eliminación",
                         options=["Por ID","Por valor en una columna","Por una condicion específica"])
if opcion_eliminar == "Por ID":
    dato=st.text_input(f"Ingrese el ID que desea buscar para eliminar (ejemplo: {ejemplo_id.get(st.session_state['archivo'])[0]})",key="registro_a_eliminar")
    if st.button("Buscar registros a eliminar"):
        if dato:
            id_columna = ejemplo_id[st.session_state['archivo']][1]

            #Reutilizo logica de eliminacion por ID pero usando pandas
            afectados = df[df[id_columna].astype(str) == dato]

            if afectados.empty:
                st.warning("No se encontraron registros")
                # Limpio las variables de sesión por si se hizo una busqueda previa
                if "afectados" in st.session_state:
                    del st.session_state["afectados"]
                if "valorID" in st.session_state:
                    del st.session_state["valorID"]
            else:
                st.session_state["del_valorID"] = dato
                st.session_state["del_afectados"] = afectados  
        else:
            st.warning("Ingrese un ID para buscar")

    if "del_afectados" in st.session_state:
        st.write("Se eliminarán los siguientes registros:")
        st.dataframe(st.session_state["del_afectados"])

        if st.button("Confirmar eliminación"):
            resultado = eli.identificador(
                st.session_state['dataset'],
                st.session_state['archivo'],
                st.session_state["del_valorID"]
            )
            st.success(resultado)
            del st.session_state["del_afectados"]
            del st.session_state["del_valorID"]
            time.sleep(2)
            st.rerun()
        

elif opcion_eliminar == "Por valor en una columna":
    col=st.selectbox("Selecciona la columna a verificar",df.columns)
    valores=st.text_area("Ingresa los valores que quiera eliminar (uno por linea):")
    valores=[val.strip() for val in valores.splitlines() if val.strip()]

    if st.button("Buscar para eliminar"):
        if not valores:
            st.warning("Ingrese valores para comenzar")
        else:
            #Reutilizo la logica del eliminar por columna
            afectados = df[df[col].astype(str).isin(valores)]
            if afectados.empty:
                st.warning("No se encontraron registros con esos valores")
            else:
                st.session_state["del_columna"] = col
                st.session_state["del_valores"] = valores
                st.session_state["del_afectados"] = afectados
    if "del_afectados" in st.session_state:
        st.write("Se eliminarán los siguientes registros:")
        st.dataframe(st.session_state["del_afectados"])
        
        if st.button("Eliminar"):
                resultado=eli.eliminar_columna(
                    st.session_state['dataset'],
                    st.session_state['archivo'],
                    st.session_state["del_columna"],
                    st.session_state["del_valores"]
                )
                if "no existe" in resultado.lower():
                    st.error(resultado)
                else:
                    st.success(resultado)
                del st.session_state["del_columna"]
                del st.session_state["del_valores"]
                del st.session_state["del_afectados"]
                time.sleep(2)
                st.rerun()
else:
    condiciones={
        "Igual":lambda a, b: a == b,
        "Diferente":lambda a, b: a!=b,
        "Mayor":lambda a, b: a > b,
        "Mayor o igual":lambda a, b: a >= b,
        "Menor":lambda a, b: a < b,
        "Menor o igual":lambda a, b: a <= b
    }

    cond=st.selectbox("Seleccione la condicion",condiciones.keys())
    col=st.multiselect("Seleccione las columnas a revisar",df.columns)
    valor=st.text_input("Escriba el dato con el que comparar")
    if st.button("Buscar para eliminar"):
        if not col:
            st.warning("Seleecione una columna")
        else:
            mask = pd.Series(False, index=df.index)

            #Reutilizo logica de eliminacion por condicion
            for columna in col:
                try:
                    serie = pd.to_numeric(df[columna])
                    valor_cmp = float(valor)
                except ValueError:
                    serie = df[columna].astype(str)
                    valor_cmp = str(valor)

                mask |= condiciones[cond](serie, valor_cmp)

            afectados=df[mask]
            if afectados.empty:
                st.warning("No se encontraron registros con esa condición")
            else:
                st.session_state["del_afectados"] = afectados
                st.session_state["del_args"] = (col, valor, cond)

    if "del_afectados" in st.session_state:
        st.write("Se eliminarán los siguientes registros:")
        st.dataframe(st.session_state["del_afectados"])
        if st.button("Confirmar eliminación"):
            cols, valor, cond = st.session_state["del_args"]
            print(cols,valor,cond)
            resultado=eli.condicion(
                st.session_state['dataset'],
                st.session_state['archivo'],
                cols,valor,cond)
            print(resultado)
            st.success(resultado)
            del st.session_state["del_afectados"]
            del st.session_state["del_args"]
            time.sleep(2)
            st.rerun()