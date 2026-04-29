
"""
    En este modulo se encuentran las funciones de validacion de los datos del dataset
"""
from pathlib import Path
import csv
import os



def ruta(dataset,archivo):

    """Funcion que obtiene la ruta hacia el dataset original"""

    raiz=Path(__file__).parent.parent
    rute_in = Path(os.path.join(raiz, 'raw_datasets', dataset, archivo))
    if not rute_in.exists():
        print(f'el archivo {rute_in} no existe')
        return None
    return rute_in

def latitud(latitude):

    """Funcion que valida la latitud de un registro"""

    if(latitude is None or latitude.strip() == ""):
        return False
    else:
        latitude=float(latitude)
        if(latitude<-90 or latitude>90):
            return True
        else:
            return False
    
def longitud(longitude):

    """Funcion que valida la longitud de un registro"""

    if(longitude is None or longitude.strip() == ""):
        return False
    else:
        longitude=float(longitude)
        if(longitude<-180 or longitude>180):
            return True
        else:
            return False

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
        print(dataset)
        for fila in datos:
            if(latitud(fila[latitude])):
                cant_invalidos+=1
                registros_incorrectos.append(fila)
            if(longitud(fila[longitude])):
                if(not (fila in registros_incorrectos)):
                    cant_invalidos+=1
                    registros_incorrectos.append(fila)

        print(f"en el dataset: {dataset} hay {cant_invalidos} coordenadas invalidas {registros_incorrectos}")
        print(" \n")

    return registros_incorrectos, cant_invalidos

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
            if(not (fila[latitude] is None or fila[latitude].strip() == "") and (fila[longitude] is None or fila[longitude].strip() == "")):
                registros_incorrectos.append(fila)
            if((fila[latitude] is None or fila[latitude].strip() == "") and not (fila[longitude] is None or fila[longitude].strip() == "")):
                registros_incorrectos.append(fila)
        print("\n")
                
        return registros_incorrectos
