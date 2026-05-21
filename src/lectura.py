"""
Módulo de lectura de datasets

Este modulo se encarga de la lectura y procesamiento basico de la informacion de cada dataset
"""
from pathlib import Path
#import csv
import os
import pandas as pd

def msj_error_archivo(archivo):
    print(f"Error: El archivo {archivo} no existe")

def obtener_ruta(nombre_dataset, nombre_archivo):

    """Obtiene la ruta de entrada del dataset original y la ruta de salida del dataset procesado"""

    raiz = Path(__file__).parent.parent
    ruta_in = Path(os.path.join(raiz, 'raw_datasets', nombre_dataset, nombre_archivo))
    ruta_out = Path(os.path.join(raiz, 'processed_datasets', f"{nombre_dataset}_procesado.csv"))

    if not ruta_in.exists():
        msj_error_archivo(nombre_archivo)
        return None, None
    return ruta_in, ruta_out

def obtener_dataset(nombre_dataset, delimitador=",", usecols=None):

    """
    Obtiene la ruta del dataset procesado y lo retorna como dataframe
    """

    raiz = Path(__file__).parent.parent
    ruta = Path(os.path.join(raiz, 'processed_datasets', f"{nombre_dataset}_procesado.csv"))

    if not ruta.exists():
        msj_error_archivo(f"{nombre_dataset}_procesado.csv")
        return None
    return pd.read_csv(ruta, sep=delimitador)

def listar_columnas(dataset,archivo,delimitador=","):
    
    """Retorna una lista con los nombres de cada columna del dataset"""
    
    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return None
    return pd.read_csv(ruta_in, sep=delimitador, nrows=0).columns.to_list() # nrows=0 para leer solo el encabezado y obtener las columnas
    
def posicion_columnas(dataset,archivo,delimitador=","):
    
    """ Retorna un diccionario con la posicion de cada columna"""
    
    columnas = listar_columnas(dataset,archivo,delimitador)
    if not columnas:
        return {}
    
    return {indice: nombre for indice,nombre in enumerate(columnas)}
    
def primeras_10_filas(dataset,archivo,delimitador=","):

    """Retorna un dataframe con las primeras 10 filas de un dataset"""

    ruta_in, _ = obtener_ruta(dataset, archivo)
    if not ruta_in:
        return None

    return pd.read_csv(ruta_in, sep=delimitador, nrows=10) # nrows=10 para leer solo las primeras 10 filas del dataset

def cant_registros(dataset,archivo,delimitador=","):

    """Retorna la cantidad de registros del dataset"""

    _, ruta = obtener_ruta(dataset,archivo)
    if not ruta:
        return 0
    
    return len(pd.read_csv(ruta, sep=delimitador, usecols=[0])) # usecols=[0] para leer solo la primera columna

def analisis_nulos(dataset, archivo, delimitador=","):
    """
    Retorna un diccionario con:
    - Cantidad de nulos por columna
    - Promedio de nulos por columna
    - Lista de columnas totalmente nulas
    """
    ruta_in, _ = obtener_ruta(dataset, archivo)
    if not ruta_in: return None

    df = pd.read_csv(ruta_in, sep=delimitador)
    total_filas = len(df)
    
    # isna() genera una mascara booleana donde True representa un valor nulo
    nulos_por_columna = df.isna().sum()
    promedio_nulos = nulos_por_columna / total_filas
    columnas_100_nulas = nulos_por_columna[nulos_por_columna == total_filas].index.tolist()

    return {
        "Cantidad nulos por columna": nulos_por_columna.to_dict(),
        "Promedio nulos por columna": promedio_nulos.to_dict(),
        "Columnas totalmente nulas": columnas_100_nulas
    }

def analisis_frecuencias(dataset, archivo, columna, delimitador=','):

    """Retorna la cantidad de valores únicos y sus frecuencias"""

    ruta_in, _ = obtener_ruta(dataset, archivo)
    if not ruta_in: return None

    # Leemos solo la columna que nos interesa
    try:
        df = pd.read_csv(ruta_in, sep=delimitador, usecols=[columna])
    except ValueError:
        return f"La columna '{columna}' no existe en el dataset"

    # Limpieza: 
    #   - dropna() para eliminar los nulos antes de limpiar
    #   - astype(str) para asegurar que todos los valores sean tratados como texto
    #   - str.strip() para eliminar espacios en blanco al inicio y al final
    serie_limpia = df[columna].dropna().astype(str).str.strip()

    # Eliminar valores que representen nulos o no aplicables, como "N/A" o "N/A N/A", sin importar mayúsculas o minúsculas
    serie_valida = serie_limpia[~serie_limpia.str.upper().isin(["N/A", "N/A N/A"])]

    frecuencias = serie_valida.value_counts()
    
    return {"Cantidad de valores distintos en la columna ingresada": len(frecuencias),
            "Frecuencias": frecuencias.to_dict()}

def valores_max_min(dataset,archivo,columna,tipo,delimitador=','):

    """
    Revisa el campo columna y dependiendo su tipo, retorna:
    - numeric (int): el valor minimo, el valor maximo y el promedio
    - text (str): cantidad de caracteres del texto mas corto y del mas largo encontrados
    - coordinate: el menor y mayor valor encontrados
        -> formato coordenada DD: (latitud,longitud) --> (41.40338,-2.17403)
    """

    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return None
    
    try:
        df = pd.read_csv(ruta_in, sep=delimitador, usecols=[columna])
    except ValueError:
        return f"La columna '{columna}' no existe en el dataset"
    
    serie = df[columna].dropna().astype(str).str.strip() # Limpieza: eliminar nulos, convertir a string y eliminar espacios en blanco
    tipo = tipo.lower() # Normalizo el tipo para manejarlo de manera consistente

    if serie.empty:
        return "El campo ingresado no contiene datos"
    
    if tipo in ("coordinate", "numeric"):
        
        serie_num = pd.to_numeric(serie, errors='coerce').dropna() # errors='coerce' convierte todo lo que no sea numérico a NaN, luego dropna() elimina esos valores
        if serie_num.empty:
            return f"No se encontraron valores numéricos válidos en la columna '{columna}'"
        
        if tipo == "coordinate":
            # 1. Convertimos a texto para analizar sus caracteres
            serie_str = serie.astype(str).str.strip()

            # 2. Aplicamos una mascara para identificar que tenga un . (obligatorio en una coordenada formato DD) y una longitud dentro de un rango razonable
            mask = serie_str.str.contains('.', regex=False) & serie_str.str.len().between(5,18)

            # 3. Convertimos a numérico solo los que pasaron la mascara, y eliminamos los no numéricos
            serie_num = pd.to_numeric(serie_str[mask], errors='coerce').dropna()

            if serie_num.empty:
                return f"No se encontraron coordenadas válidas en la columna '{columna}'"
            
            return {
                "Coordenada minima": float(serie_num.min()),
                "Coordenada maxima": float(serie_num.max())
            }
        stats = {
            "Valor minimo": float(serie_num.min()),
            "Valor maximo": float(serie_num.max())
        }
        if tipo == "numeric":
            stats["Promedio"] = float(serie_num.mean())
        return stats
    
    elif tipo == "text":
        longitud_textos = serie.astype(str).str.strip().str.len() # Limpieza adicional: eliminar espacios en blanco antes de contar caracteres
        return {
            "Longitud del texto más corto": int(longitud_textos.min()),
            "Longitud del texto más largo": int(longitud_textos.max())
        }
    
    else:
        return f"Tipo '{tipo}' no es válido. Por favor ingrese 'numeric', 'text' o 'coordinate'."