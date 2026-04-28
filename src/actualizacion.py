from lectura import obtener_ruta
import csv

"""
Este modulo se encarga de la modificación de registros existentes dentro de un dataset
"""

def buscar_registros(dataset,archivo,columnas,delimitador=","):

    """Busca registros dentro de un dataset que cumplan con todas condiciones ingresadas por parametro.
    'columnas' es un diccionario con el formato {columna:valor} donde columna es el nombre de la columna a comparar 
    y valor es el valor que debe tener esa columna para que el registro sea incluido en los resultados.
    """

    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return []
    resultados = []

    with open(ruta_in, 'r', encoding='utf-8') as archivo_in:
        lector = csv.DictReader(archivo_in, delimiter=delimitador)
        for fila in lector:
            if all(str(fila[columna]).strip().upper() == str(valor).strip().upper() for columna, valor in columnas.items()):
                resultados.append(fila)
        return resultados