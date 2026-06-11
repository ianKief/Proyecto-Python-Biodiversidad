import streamlit as st
import pandas as pd
import os
import csv
from dateutil import parser
from src.insercion import validar_registro
import pycountry
from babel import Locale
from src.actualizacion import actualizar_multiples_campos
import src.eliminacion as eli

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
                else:
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

st.subheader("Buscar un registro por ID")
registro_id=st.text_input(f"Ingrese el ID que desea buscar (ejemplo: {ejemplo_id.get(st.session_state['archivo'])[0]})", key="registro_a_buscar")

try:
    if st.button("Buscar Registro"):
        id_columna=ejemplo_id.get(st.session_state['archivo'])[1]
        registro_encontrado=df[df[id_columna].astype(str)==registro_id]
        if registro_encontrado.empty:
            st.warning("No se encontró ningún registro con ese ID.")
        else:
            st.session_state["registro_encontrado"]=registro_encontrado
            st.success("Registro encontrado:")

except Exception as e:
    st.error(f"Ocurrió un error al buscar el registro: {e}")

#Ejercicio 4.C
st.subheader("Actualizar registro encontrado")
st.write("Una vez relizada la busqueda del registro aca podra modificar los campos deseados")

if "registro_encontrado" in st.session_state:
    original=dict(st.session_state["registro_encontrado"].iloc[0])
    editado=st.data_editor(st.session_state["registro_encontrado"],key="editor")


if st.button("Validar registro encontrado y modificarlo"):
    editado_dict=dict(editado.iloc[0])
    cambios={}
    juntos={"campos":[],
                "original":[],
                "editado":[]
                }

    if not editado_dict:
        st.warning("Primero busque el registro a modificar")
    else:
        for campo in original:
            if pd.isna(editado_dict[campo]):
                editado_dict[campo]=original[campo]
                juntos["campos"].append(campo)
                juntos["original"].append(original[campo])
                juntos["editado"]. append(original[campo])
                continue

            if editado_dict[campo]!=original[campo]:
                cambios[campo]=editado_dict[campo]

            juntos["campos"].append(campo)
            juntos["original"].append(original[campo])
            juntos["editado"]. append(editado_dict[campo])
            
        columna_ID=ejemplo_id[st.session_state['archivo']][1]
        st.write(cambios)
        if not cambios:
            st.write("No hubieron modificaciones")
        else:
            try:
                st.write(original[columna_ID])
                actualizar=(actualizar_multiples_campos(st.session_state['dataset'],st.session_state['archivo'],columna_ID,original[columna_ID],cambios))
                if actualizar == "Columnas actualizadas exitosamente":
                    tabla=pd.DataFrame(juntos)
                    st.table(tabla)
            except Exception as e:
                st.error(f"Hubo un error a la hora de actualizar el registro, {e}")

#Ejercicio 4.D
st.subheader("Eliminar un registro")
st.write("A continuacion podra elegir la forma en la que desea eliminar un registro del dataset")
opcion_eliminar=st.radio(label="Seleccione el método de eliminación",
                         options=["Por ID","Por valor en una columna","Por una condicion específica"])
if opcion_eliminar == "Por ID":
    dato=st.text_input(f"Ingrese el ID que desea buscar para eliminar (ejemplo: {ejemplo_id.get(st.session_state['archivo'])[0]}",key="registro_a_eliminar")
    if st.button("Buscar registros a eliminar"):
        if dato:

            id_columna = ejemplo_id[st.session_state['archivo']][1]

            #Reutilizo logica de eliminacion por ID pero usando pandas
            afectados = df[
                df[id_columna].astype(str) == dato
            ]

            if afectados.empty:
                st.warning("No se encontraron registros")
                # Limpio las variables de sesión por si se hizo una busqueda previa
                if "afectados" in st.session_state:
                    del st.session_state["afectados"]
                if "valorID" in st.session_state:
                    del st.session_state["valorID"]
            else:
                st.session_state["valorID"] = dato
                st.session_state["afectados"] = afectados

                
        else:
            st.warning("Ingrese un ID para buscar")

        if "afectados" in st.session_state:
            afectados = st.session_state["afectados"]
            st.write(
                    f"Se eliminarán {len(afectados)} registros"
                )
            st.dataframe(afectados)

            if st.button("Confirmar eliminación"):
                resultado = eli.identificador(
                    st.session_state['dataset'],
                    st.session_state['archivo'],
                    st.session_state["valorID"]
                )

                st.success(resultado)
                del st.session_state["afectados"]
                del st.session_state["valorID"]
        

elif opcion_eliminar == "Por valor en una columna":
    col=st.selectbox("Selecciona la columna a verificar",df.columns)
    valores=st.text_area("Ingresa los valores que quiera eliminar (uno por linea):")
    valores=valores.splitlines()

    if st.checkbox("Eliminar"):
        if not valores:
            st.warning("Ingrese valores para comenzar")
        else:
            #Reutilizo la logica del eliminar por columna
            afectados = df[df[col].astype(str).isin(valores)]
            st.write(f"Seliminaran {len(afectados)} registros")
            st.session_state["afectados"] = afectados
            st.dataframe(afectados)

            if "afectados" in st.session_state:
                if st.button("Eliminar"):
                    resultado=eli.eliminar_columna(
                        st.session_state['dataset'],
                        st.session_state['archivo'],
                        col,
                        valores
                        )
                    
                    st.success(resultado)
else:
    condiciones={
        "==":lambda a, b: a == b,
        "!=":lambda a, b: a!=b,
        ">":lambda a, b: a > b,
        ">=":lambda a, b: a >= b,
        "<":lambda a, b: a < b,
        "<=":lambda a, b: a <= b
    }

    cond=st.selectbox("Seleccione la condicion",condiciones.keys())
    col=st.multiselect("Seleccione las columnas a revisar",df.columns)
    valor=st.text_input("Escriba el dato con el que comparar")
    if not col:
        st.warning("Seleecione una columna")
    else:
        if st.button("Buscar"):
            mask = pd.Series(False, index=df.index)

            #Reutilizo logica de eliminacion por condicion
            for columna in col:
                try:
                    serie = pd.to_numeric(df[columna])
                    valor_cmp = float(valor)
                except ValueError:
                    try:
                        serie=parser.parser(df[columna])
                        valor_cmp=parser.parser(valor)
                    except ValueError:
                            serie = df[columna].astype(str)
                            valor_cmp = str(valor)

                mask |= condiciones[cond](serie, valor_cmp)

            afectados=df[mask]
            st.session_state["afectados"] = afectados
            st.write(f"Se eliminaran {len(afectados)}")
            st.write(afectados)

            if "afectados" in st.session_state:
                resultado=eli.condicion(st.session_state['dataset'],st.session_state['archivo'],col,valor,cond)
                st.success(resultado)