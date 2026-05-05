
"""
    En este modulo se encuentran las funciones de validacion de los datos del dataset
"""
from pathlib import Path
import csv
import os
import pycountry
import re
from dateutil import parser
from datetime import datetime
from lectura import cant_registros


def ruta(dataset,archivo):

    """Funcion que obtiene la ruta hacia el dataset original"""

    raiz=Path(__file__).parent.parent
    rute_in = Path(os.path.join(raiz, 'raw_datasets', dataset, archivo))
    if not rute_in.exists():
        print(f'el archivo {rute_in} no existe')
        return None
    return rute_in

def verificar_rango(dato,max,min):

    """Verifica si el dato del campo esta vacio o no y lo verifica si tiene un valor"""

    if(dato is None or dato.strip() == ""):
        return True
    else:
        dato=float(dato)
        if(dato <=max and dato>=min):
            return False
        else:
            return True

def coordenadas(dataset,archivo,delimitadror=","):

    """Valida la informacion de los campos decimalLatitude|latitudeDecimal y decimalLongitude|longitudeDecimal, y retorna 
       cantidad de registros invalidos y los registros con coordenadas invalidas
    """

    rute_in=ruta(dataset,archivo)
    if not rute_in:
        return None
    with open (rute_in,'r',encoding='utf-8') as archivo:
        cant_invalidos=0
        registros_incorrectos=[]
        datos=csv.DictReader(archivo,delimiter=delimitadror)

        latitude=[datos for datos in datos.fieldnames if "latitude" in datos.lower()][0]
        longitude=[datos for datos in datos.fieldnames if "longitude" in datos.lower()][0]

        maximo_latitud=90
        minimo_latitud=-90
        maximo_longitud=180
        minimo_longitud=-180

        print(dataset)
        for fila in datos:
            if(verificar_rango(fila[latitude],maximo_latitud,minimo_latitud)):
                cant_invalidos+=1
                registros_incorrectos.append(fila)
            if(verificar_rango(fila[longitude],maximo_longitud,minimo_longitud)):
                if(not (fila in registros_incorrectos)):
                    cant_invalidos+=1
                    registros_incorrectos.append(fila)

        print(f"en el dataset: {dataset} hay {cant_invalidos} coordenadas invalidas")
        print(" \n")

    return registros_incorrectos, cant_invalidos

def no_existe_dato(dato):

    """Funcion que verifica si el campo esta vacio o no"""

    if(dato is None or dato.strip()==""):
        return True
    else:
        return False

def existe(dataset,archivo,delimitador=","):

    """Funcion que valida la existencia de latitud pero no longitud, y longitud pero no latitud en los registros del dataset"""

    rute_in=ruta(dataset,archivo)
    if not rute_in:
        return None
    
    with open(rute_in,'r',encoding='utf-8') as archivo:
        datos=csv.DictReader(archivo,delimiter=delimitador)
        registros_incorrectos=[]
        latitude=[datos for datos in datos.fieldnames if "latitude" in datos.lower()][0]
        longitude=[datos for datos in datos.fieldnames if "longitude" in datos.lower()][0]
        print(dataset)
        for fila in datos:

            #Latitud existe pero longitud no
            if(not (no_existe_dato(fila[latitude])) and (no_existe_dato(fila[longitude]))):
                registros_incorrectos.append(fila)

            #Latitud no existe pero longitud si
            elif((no_existe_dato(fila[latitude])) and not (no_existe_dato(fila[longitude]))):
                registros_incorrectos.append(fila)
                
        print("\n")
                
        return registros_incorrectos

def duplicados(dataset,archivo,delimitador=","):

    """Funcion que revisa si hay duplicados en el archivo y los IDs repetidos"""

    rute_in=ruta(dataset,archivo)
    if not rute_in:
        return None
    
    with open(rute_in,'r',encoding='utf-8') as archivo:
        datos=csv.DictReader(archivo,delimiter=delimitador)
        dupli=0
        reg_duplicados=[]
        registros=set()
        campo_ID=datos.fieldnames[0]
        for fila in datos:
            if (fila[campo_ID] in registros):
                if(fila[campo_ID] in reg_duplicados):
                    dupli+=1
                else:
                    dupli+=1
                    reg_duplicados.append(fila[campo_ID])
            else:
                registros.add(fila[campo_ID])
        print(f"en el dataset: {dataset} hay {dupli} registros duplicados, con los siguientes ID: {reg_duplicados}")
        print("\n")


    return reg_duplicados

def parece_fecha(texto):

    """Funcion que se fija si el dato pasado es una fecha"""

    patrones = [
        r"\d{4}-\d{2}-\d{2}",          # 2020-04-17
        r"\d{2}/\d{2}/\d{4}",          # 31/03/2018
        r"\d{4}/\d{2}/\d{2}",          # 2018/03/31
        r"\d{2}:\d{2}:\d{2}",          # 08:09:00
        r"T\d{2}:\d{2}:\d{2}",         # ISO
    ]
    return any(re.search(p, texto) for p in patrones)

def corregir_12h(match):

    """Funcion que pasa de 16 PM (invalido) a 04 PM (valido)"""

    hora = int(match.group(1))
    minutos = match.group(2)
    segundos = match.group(3)
    ampm = match.group(4).upper()

    if(hora>12):
        hora-=12

    if minutos and segundos:
        return f"{hora:02}:{minutos}:{segundos} {ampm}"
    elif minutos:
        return f"{hora:02}:{minutos} {ampm}"
    else:
        return f"{hora:02} {ampm}"
    
def puntos(match):

    """Funcion que reemplaza los "." en una hora por ":" """

    h = match.group(1)
    m = match.group(2)
    s = match.group(3)

    if s:
        return f"{h}:{m}:{s}"
    return f"{h}:{m}"


def limpiar(fecha,estandares):

    """Funcion que limpia el dato para asi ver si se puede interpretar como una fecha"""

    if(len(fecha)>30):
        return None
    else:
        for valor in estandares.keys():
            if(valor in fecha):
                #Reemplaza las zonas horarias (ARST,PST,WET,etc) por su valor
                fecha = fecha.replace(valor, estandares[valor])

        #Elimina caracteres invicibles (LRM o RLM)
        fecha = re.sub(r"[\u200e\u200f\u202a-\u202e]", "", fecha)

        #Borra los parentesis
        fecha=re.sub(r"\(.*?\)", "",fecha)

        #Elimina el exceso de espacios 
        fecha=re.sub(r"\s+", " ", fecha).strip()

        #Normaliza PM o AM mal escritos, ej: p.m, p m
        fecha=re.sub(r"\b(p\.?\s*m\.?)\b", "PM", fecha, flags=re.IGNORECASE)
        fecha=re.sub(r"\b(a\.?\s*m\.?)\b", "AM", fecha, flags=re.IGNORECASE)

        #Agrega un espacio entre PM/AM y el tiempo, ej: 05:03PM lo pasa a 05:03 PM 
        fecha = re.sub(r"(\d{2})(AM|PM)\b", r"\1 \2", fecha, flags=re.IGNORECASE)

        #Elimina la abreviacion hs de la hora
        fecha = re.sub(r"\bhs\b", "", fecha, flags=re.IGNORECASE)

        #reemplaza los divisiones del tiempo invalidas (".",";","_"), ej: 05.06.03, 05;06;03, 05_06_03 lo pasa a 05:06:03
        fecha = re.sub(r"\b(\d{1,2})\.(\d{2})(?:\.(\d{2}))?\b",puntos,fecha)
        fecha = re.sub(r"\b(\d{1,2})\;(\d{2})(?:\;(\d{2}))?\b",puntos,fecha)
        fecha = re.sub(r"\b(\d{1,2})\_(\d{2})(?:\_(\d{2}))?\b",puntos,fecha)

        #Limpia los espacios en el tiempo, ej: 11:  08
        fecha=re.sub(r"(\d{1,2})\s*:\s*(\d{2})", r"\1:\2", fecha)

        #Elimina ":" adelante de la hora, ej: :05:03 lo pasa a 05:03
        fecha = re.sub(r"\s:(\d{1,2}:\d{2})", r" \1", fecha)

        #Elimina letras antes del UTC o el valor de la zona, ej: DE -0300
        fecha = re.sub(r"\b[A-Za-z]+(?=[+-]\d{4}\b)", "", fecha)
        fecha = re.sub(r"\b[A-Za-z]+\b(?=\s+UTC\b)", "", fecha)

        #Pasa el tiempo a un formato AM/PM valido, ej: 17 PM lo pasa a 05 PM
        fecha = re.sub(r"\b(1[3-9]|2[0-3])(?::([0-5]\d))?(?::([0-5]\d))?\s*(AM|PM)\b",corregir_12h,fecha,flags=re.IGNORECASE)

        #Reemplaza la cadena de 0 por una con signo positivo
        if re.search(r"\b0000$", fecha):
            fecha = fecha[:-4] + "+0000"

        return fecha

    
def fechas(dataset,archivo,delimitador=","):

    """Funcion que revisa el formato de las fechas del dataset"""

    rute_in=ruta(dataset,archivo)
    if not rute_in:
        return None
    
    registros=[]
    with open(rute_in,'r',encoding="utf-8") as archivo:
        datos=csv.DictReader(archivo,delimiter=delimitador)

        #Zonas horarias que aparecen y no las interpreta el parser
        tzinfos = {
                "HST": "-1000",
                "SST": "-1100",  
                "ART": "-0300",
                "ARST": "-0200",
                "PST": "-0800",
                "PDT": "-0700",
                "CET": "+0100",
                "CEST": "+0200",
                "EST": "-0500",
                "EDT": "-0400",
                "WET": "0000",
                "WEST": "+0100",
                "SAST": "+0200",
                "ACDT": "+1030",
                "ACST": "+0930",
                "CDT": "-0500",
                "CST": "-0600",
                "BST": "+0100",
                "MST": "-0700",
                "MDT": "-0600",
                "AEST": "+1000",
                "AEDT": "+1100",
                "NZDT": "+1300",
                "NZST": "+1200",
                "BRT": "-0300",
                "EET": "+0200",
                "EEST": "+0300",
                "BRT": "-0300",
                "BRST": "-0200",
                "MSK": "+0300",
                "IST":"+0530",
                "NST":"-0330",
                "NDT":"-0230",
                "AKST":"-0900",
                "CMT":"-0500",
                "AWST":"+0800",
                "AST":"-0400",
                "COT":"-0500",
                "IDT":"+0300"
                }

        print(dataset)
        fecha_actual=datetime.now().year
        for fila in datos:
            for campos in fila:
                if not (parece_fecha(fila[campos])):
                    continue
                else:
                    fecha=limpiar(fila[campos],tzinfos)
                    if(fecha==None):
                        continue
                    else:
                        try:
                            fecha=parser.parse(fecha)
                        except:
                            registros.append(fila)
                            continue

                    if (fecha.year > fecha_actual):
                        if(fila not in registros):
                            registros.append(fila)


    return registros

def incertidumbre(dataset,archivo,delimitador=","):

    """Funcion que guarda los registros en los que el valor del campo pedido no es un numero, es negativo o es muy alto(ejemplo>1000)"""

    rute_in=ruta(dataset,archivo)
    if not rute_in:
        return None
    
    with open(rute_in,'r',encoding='utf-8') as archivo:
        datos=csv.DictReader(archivo,delimiter=delimitador)
        invalidos={"no_numeros":[],
                   "negativos":[],
                   "muy_alto":[]
                  }
        if("coordinateUncertaintyInMeters" not in datos.fieldnames):
            print(f"El campo coordinateUncertaintyInMeters no existe en {dataset}")
        else:
            for fila in datos:
                if (no_existe_dato(fila["coordinateUncertaintyInMeters"])):
                    invalidos["no_numeros"].append(fila)
                else:
                    valor=float(fila["coordinateUncertaintyInMeters"])
                    if(valor <0):
                        invalidos["negativos"].append(fila)
                    elif(valor>1000):
                        invalidos["muy_alto"].append(fila)
    return invalidos

def max_min(dataset,archivo,delimitador=","):

    """Funcion que setea rangos propios y verifica que los datos esten dentro de ese rango"""

    rute_in=ruta(dataset,archivo)
    if not rute_in:
        return None
    
    with open(rute_in,'r',encoding='utf-8') as archivo:
        datos=csv.DictReader(archivo,delimiter=delimitador)
        registros_invalidos=[]

        latitude=[datos for datos in datos.fieldnames if "latitude" in datos.lower()][0]
        longitude=[datos for datos in datos.fieldnames if "longitude" in datos.lower()][0]

        maximo_latitud=70
        minimo_latitud=-70
        maximo_longitud=160
        minimo_longitud=-160

        print(dataset)
        for fila in datos:
            if(verificar_rango(fila[latitude],maximo_latitud,minimo_latitud)):
                registros_invalidos.append(fila)

            if(verificar_rango(fila[longitude],maximo_longitud,minimo_longitud)):
                if(fila not in registros_invalidos):
                    registros_invalidos.append(fila)

    return registros_invalidos


def country(dataset,archivo,delimitador=","):

    """Funcion que se fija el valor del campo countryCode"""

    rute_in=ruta(dataset,archivo)
    if not rute_in:
        return None
    
    with open(rute_in,'r',encoding='utf-8') as archivo:
        datos=csv.DictReader(archivo,delimiter=delimitador)
        registros_invalidos=[]
        
        print(dataset)
        if("countryCode" not in datos.fieldnames):
            print(f"El campo countryCode no existe en {dataset}")
            print(" \n")
            return None
        else:
            for fila in datos:
                pais=pycountry.countries.get(alpha_2=fila["countryCode"])
                if(fila["countryCode"]is None or fila["countryCode"].strip() == ""):
                    registros_invalidos.append(fila)
                    print("Campo vacio")
                elif(pais is None):
                    registros_invalidos.append(fila)
                    print(f"codigo no valido ({fila['countryCode']})")

    return registros_invalidos

def informacion_taxonomica(dataset,archivo,delimitador=","):
    rute_in=ruta(dataset,archivo)
    if not rute_in:
        return None
    #La informacion necesaria: familia, reino, genero, filo, especie, dominio, orden, clase
    taxonomia=["family","kingdom","genus","phylum","scientificName","higherClassification","order","class"]
    
    with open(rute_in,encoding="utf8") as archivo:
        datos=csv.DictReader(archivo,delimiter=delimitador)
        registros_invalidos=[]
        for campo in taxonomia:
            if(campo not in datos.fieldnames):
                continue

            for fila in datos:
                if no_existe_dato(fila[campo]):
                    if not (fila in registros_invalidos):
                        registros_invalidos.append(fila)

    return registros_invalidos



def resumen(dataset,archivo,delimitador=","):

    cant=cant_registros(dataset,archivo,delimitador)
    dupli=duplicados(dataset,archivo,delimitador)
    taxonomica=informacion_taxonomica(dataset,archivo,delimitador)
    coord_invalidas=coordenadas(dataset,archivo,delimitador)
    fecha=fechas(dataset,archivo,delimitador)

    resumen_calidad={"cantidad":cant,
                     "duplicados":dupli,
                     "taxonomia":taxonomica,
                     "coordenadas":coord_invalidas,
                     "fechas":fecha}
    
    return resumen_calidad


def coordenada_completa(dataset,archivo,dato,maximo,minimo,delimitador=","):

    """Funcion que recibe que coordenada se quiere verificar (latitud o longitud) y el rango del mismo (delimitado por maximo y minimo)"""

    rute_in=ruta(dataset,archivo)
    if not rute_in:
        return None
    
    with open (rute_in,'r',encoding='utf-8') as archivo:
        datos=csv.DictReader(archivo,delimiter=delimitador)
        campo=[datos for datos in datos.fieldnames if dato in datos.lower()][0]
        maximo_seteado=maximo-20
        minimo_seteado=minimo+20
        registros=[]

        for fila in datos:

            #Verifico si existe el dato, si esta dentro de su rango original y si esta dentro del rango que yo estableci
            if not(verificar_rango(fila[campo],maximo,minimo)):
                if not(verificar_rango(fila[campo],maximo_seteado,minimo_seteado)):
                    continue
            
            registros.append(fila)

    return registros
