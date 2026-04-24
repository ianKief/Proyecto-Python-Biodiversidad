"""
Módulo de lectura de datasets

Este modulo se encarga de la lectura y procesamiento basico de la informacion de cada dataset
"""
from pathlib import Path
import csv

def obtener_ruta(nombre_dataset, nombre_archivo):

    """Obtiene la ruta de entrada del dataset original y la ruta de salida del dataset procesado"""

    raiz = Path(__file__).parent.parent
    ruta_in = raiz / 'raw_datasets' / nombre_dataset / nombre_archivo
    ruta_out = raiz / 'processed_datasets' / f"{nombre_dataset}_procesado.csv"

    if not ruta_in.exists():
        print(f"Error: El archivo {ruta_in} no existe.")
        return None, None
    return ruta_in, ruta_out

def listar_columnas(dataset,archivo,delimitador=","):
    
    """Retorna una lista con los nombres de cada columna del dataset"""
    
    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return None
    with open(ruta_in, "r", encoding='utf-8') as archivo_in:
        return list(csv.DictReader(archivo_in,delimiter=delimitador).fieldnames)
    
def posicion_columnas(dataset,archivo,delimitador=","):
    
    """ Retorna un diccionario con la posicion de cada columna"""
    
    columnas = listar_columnas(dataset,archivo,delimitador)
    if not columnas:
        return {}
    
    return {indice: nombre for indice,nombre in enumerate(columnas)}
    
def imprimir_primeras_10_filas(dataset,archivo,delimitador=","):

    """Imprime las primeras 10 filas de un dataset en un archivo .csv"""

    ruta_in, ruta_out = obtener_ruta(dataset, archivo)
    if not ruta_in or not ruta_out:
        return None

    with open(ruta_in, 'r', encoding='utf-8') as archivo_in:
        lector = csv.DictReader(archivo_in, delimiter=delimitador)

        with open(ruta_out, 'w', encoding='utf-8', newline='') as archivo_out:
            escritor = csv.DictWriter(archivo_out, fieldnames=lector.fieldnames, delimiter=",")
            escritor.writeheader()
            
            for i, fila in enumerate(lector):
                if i < 10:
                    escritor.writerow(fila)
                else:
                    break

def cant_registros(dataset,archivo,delimitador=","):

    """Retorna la cantidad de registros del dataset"""

    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return 0
    with open(ruta_in,'r',encoding='utf-8') as archivo_in:
        lector = csv.reader(archivo_in,delimiter=delimitador)
        for i,fila in enumerate(lector):
            continue
        return i

def columnas_con_nulo(dataset,archivo,delimitador=","):
    
    """Retorna la cantidad de registros nulos que tiene cada columna del dataset"""

    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return None

    with open(ruta_in,'r',encoding='utf-8') as archivo_in:
        lector = csv.DictReader(archivo_in,delimiter=delimitador)
        #Creo un diccionario para manejar un contador con la cantidad de nulos que tiene cada columna
        columnas_sucias = {col:0 for col in lector.fieldnames}
        
        for fila in lector:
            for columna,valor in fila.items():
                if not valor or valor.strip()=="":
                    columnas_sucias[columna] += 1

    return columnas_sucias

def promedio_nulos(dataset,archivo,delimitador=','):

    """Retorna el promedio de registros nulos para cada columna del dataset"""

    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return "No se encontro el archivo ingresado"
    
    
    cant_reg = cant_registros(dataset,archivo,delimitador)
    columnas = columnas_con_nulo(dataset,archivo,delimitador)
    if not cant_reg or not columnas:
        return "No se pudo calcular el promedio de nulos"
    return {columna: (columnas[columna]/cant_reg) for columna in columnas}