"""
Módulo de lectura de datasets

Este modulo se encarga de la lectura y procesamiento basico de la informacion de cada dataset
"""
from pathlib import Path
import csv
import os

def obtener_ruta(nombre_dataset, nombre_archivo):

    """Obtiene la ruta de entrada del dataset original y la ruta de salida del dataset procesado"""

    raiz = Path(__file__).parent.parent
    ruta_in = Path(os.path.join(raiz, 'raw_datasets', nombre_dataset, nombre_archivo))
    ruta_out = Path(os.path.join(raiz, 'processed_datasets', f"{nombre_dataset}_procesado.csv"))

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

    cant_reg = cant_registros(dataset,archivo,delimitador)
    columnas = columnas_con_nulo(dataset,archivo,delimitador)
    if not cant_reg or not columnas:
        return "No se pudo calcular el promedio de nulos"
    return {columna: (columnas[columna]/cant_reg) for columna in columnas}

def valores_dif_columna(dataset,archivo,columna,delimitador=','):
    
    """Retorna la cantidad de valores distintos que tiene la columna ingresada por parametro
    
    Si la columna no existe, se informa la situación"""

    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return "No se encontro el archivo ingresado"
    
    with open(ruta_in,'r',encoding='utf-8') as archivo_in:
        lector = csv.DictReader(archivo_in,delimiter=delimitador)
        if columna not in lector.fieldnames:
            return f"La columna '{columna}' no existe en el dataset"
        
        valores_distintos = set()
        for fila in lector:
            valor = fila[columna].strip() #Limpiar el valor para que sea consistente
            if valor:  #Ignorar valores vacíos
                valores_distintos.add(valor)

    return f"La columna '{columna}' tiene {len(valores_distintos)} valores distintos"

def frecuencia_valores_columna(dataset,archivo,columna,delimitador=','):
    
    """Retorna un diccionario con la frecuencia de cada valor distinto que tiene la columna ingresada por parametro
    
    Si la columna no existe, se informa la situación"""

    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return "No se encontro el archivo ingresado"
    
    with open(ruta_in,'r',encoding='utf-8') as archivo_in:
        lector = csv.DictReader(archivo_in,delimiter=delimitador)
        if columna not in lector.fieldnames:
            return f"La columna '{columna}' no existe en el dataset"
        
        frecuencia_valores = {}
        valores_invalidos = {"N/A", "N/A N/A"}
        for fila in lector:
            valor = fila[columna].strip() #Limpiar el valor para que sea consistente
            if valor and valor.upper() not in valores_invalidos:  #Ignorar valores vacíos y no válidos
                frecuencia_valores[valor] = frecuencia_valores.get(valor, 0) + 1

    return frecuencia_valores

def columnas_nulas(dataset,archivo,delimitador=','):
    
    """Retorna las columnas que tienen todos sus registros nulos"""

    columnas = columnas_con_nulo(dataset,archivo,delimitador)
    if not columnas:
        return "No se pudo determinar las columnas nulas"
    
    cant_reg = cant_registros(dataset,archivo,delimitador)
    return list(columna for columna, nulos in columnas.items() if nulos == cant_reg)

def valores_max_min(dataset,archivo,columna,tipo,delimitador=','):

    """
    Revisa el campo columna y dependiendo su tipo, retorna:
    - numeric (int): el valor minimo, el valor maximo y el promedio
    - text (str): cantidad de caracteres del texto mas corto y del mas largo encontrados
    - coordinate: el menor y mayor valor encontrados
        -> formato coordenada DD: (latitud,longitud) --> (41.40338,-2.17403)
    """

    def es_coord_valida(valor):
        
        """Revisa que el valor ingresado por parametro sea una coordenada en formato DD"""
        if len(valor) not in range(5,19): # Cant total de caracteres debe ser entre 5 y 20
            return False
        test_chars = valor.replace(".","").replace("-","")
        if not test_chars.isdigit(): # Quito puntos y - a ver si contiene otros caracteres (que serian invalidos)
            return False
        if "." not in valor: # Chequeo que contenga el . obligatorio
            return False
        return True


    ruta_in, _ = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return "No se encontro el archivo ingresado"
    
    # Variables de seguimiento
    min_val = float('inf')
    max_val = float('-inf')
    suma_total = 0
    contador = 0
    tipo = tipo.lower() # Normalizo el tipo para manejarlo de manera consistente
    
    if tipo not in ("coordinate", "numeric", "text"):
        return "El tipo ingresado no es valido"
    
    with open(ruta_in,'r',encoding='utf-8') as archivo_in:
        lector = csv.DictReader(archivo_in,delimiter=delimitador)
        
        if columna not in lector.fieldnames:
            return "La columna ingresada no existe en el dataset"
        
        for fila in lector:
            valor = fila[columna].strip() #Limpiar el valor para que sea consistente
            if not valor:
                continue
            
            if tipo == "coordinate":
                if es_coord_valida(valor):
                    num = float(valor)
                    min_val = min(min_val, num)
                    max_val = max(max_val, num)
            
            elif tipo == "numeric":
                try:
                    num = float(valor)
                    min_val = min(min_val, num)
                    max_val = max(max_val, num)
                    suma_total += num
                    contador += 1
                except ValueError:
                    continue
            
            elif tipo == "text":
                min_val = min(min_val, len(valor))
                max_val = max(max_val, len(valor))
    
    if min_val == float('inf'):
        return "No se encontro ningun valor valido en la columna ingresada"
    
    if tipo == "numeric":
        promedio = suma_total / contador if contador > 0 else 0
        return {"Valor minimo": min_val, "Valor maximo": max_val, "Promedio": promedio}
    
    elif tipo == "coordinate":
        return {"Coordenada minima": min_val, "Coordenada maxima": max_val}
    
    elif tipo == "text":
        return {"Texto mas corto": int(min_val), "Texto mas largo": int(max_val)}