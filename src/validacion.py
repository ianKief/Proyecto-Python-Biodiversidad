
"""
    En este modulo se encuentran las funciones de validacion de los datos del dataset
"""
from pathlib import Path
import csv
import os
import pycountry



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
