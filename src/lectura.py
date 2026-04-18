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

def imprimir_primeras_10_filas(dataset,archivo,delimitador=","):

    """Imprime las primeras 10 filas de un dataset en un archivo .csv"""

    ruta_in, ruta_out = obtener_ruta(dataset, archivo)
    if not ruta_in or not ruta_out:
        return None

    with open(ruta_in, 'r', encoding='utf-8') as archivo_in:
        lector = csv.DictReader(archivo_in, delimiter=delimitador)

        with open(ruta_out, 'w', encoding='utf-8', newline='') as archivo_out:
            escritor = csv.DictWriter(archivo_out, fieldnames=lector.fieldnames, delimiter=delimitador)
            escritor.writeheader()
            
            for i, fila in enumerate(lector):
                if i < 10:
                    escritor.writerow(fila)
                else:
                    break