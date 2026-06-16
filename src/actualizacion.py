import csv
import os
import pycountry
from datetime import datetime
from dateutil import parser
from .lectura import obtener_ruta
from . import validacion
from . import logger

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

def actualizar_registro(dataset,archivo,id,valorID,columna,valor,delimitador=","):

    """Actualiza el valor de una columna para un registro específico identificado por 'id'.
    'id' es el nombre de la columna que identifica al registro a actualizar y 'valorID' es el valor de esa columna.
    'columna' es el nombre de la columna a actualizar y 'valor' es el nuevo valor que se asignará a esa columna.
    """

    ruta_in, ruta_out = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return "No se encontro el archivo ingresado"

    actualizado = False
    ruta_tmp = str(ruta_out) + '.tmp'

    # Primero se lee el archivo original en busqueda del registro que se quiere modificar, verificando que existan el registro y la columna a modificar
    
    try:
        with open(ruta_in, 'r', encoding='utf-8') as archivo_in, \
             open(ruta_tmp, 'w', encoding='utf-8', newline='') as archivo_out:
        
            lector = csv.DictReader(archivo_in, delimiter=delimitador)
            campos = lector.fieldnames
        
            if not id in campos:
                return "La columna de identificación no existe"
            if not columna in campos:
                return "La columna a actualizar no existe"
            
            escritor = csv.DictWriter(archivo_out, fieldnames=campos, delimiter=",")
            escritor.writeheader()

            for fila in lector:
                if str(fila[id]) == str(valorID):
                    fila_mod = fila.copy()
                    fila_mod[columna] = valor
                    errores = []
                    col = columna.lower()
                    if "latitude" in col:
                        try:
                            if validacion.verificar_rango(fila_mod[columna],90,-90):
                                errores.append(f"Latitud {fila_mod[columna]} fuera de rango")
                        except ValueError:
                            errores.append("Latitud debe ser numerica")
                    elif "longitude" in col:
                        try:
                            if validacion.verificar_rango(fila_mod[columna],180,-180):
                                errores.append(f"Longitud {fila_mod[columna]} fuera de rango")
                        except ValueError:
                            errores.append("Longitud debe ser numerica")
                    
                    # Crea una lista con todas las columnas que contienen latitud o longitud en su nombre
                    # Toma la primera coincidencia que encuentra o devuelve None si no encuentra ninguna
                    lat = next((c for c in campos if "latitude" in c.lower()), None)
                    lon = next((c for c in campos if "longitude" in c.lower()), None)
                    if lat and lon:
                        # Verifica que las se ingresen datos en ambas columnas
                        tiene_lat = bool(fila_mod[lat] and str(fila_mod[lat].strip())) # La primera condicion es para evitar errores si el valor es None
                        tiene_lon = bool(fila_mod[lon] and str(fila_mod[lon].strip()))
                        if tiene_lat != tiene_lon:
                            errores.append("Error: Los cambios dejan una coordenada vacia y otra con valor")
                    
                    if errores:
                        raise ValueError(f"Errores encontrados: {', '.join(errores)}")
                    
                    fila = fila_mod
                    actualizado = True
                
                escritor.writerow(fila)
        
        if not actualizado:
            if os.path.exists(ruta_tmp):
                os.remove(ruta_tmp)
                logger.log_error(dataset,"UPDATE")
                return "No se encontro el registro con el id ingresado"
        
        # Si todo sale bien, el archivo temporal con las modificaciones reemplaza al original
        os.replace(ruta_tmp, ruta_out)
        logger.log(dataset, "UPDATE", 1)
        return "Columna actualizada exitosamente"

    except Exception as e:
        if os.path.exists(ruta_tmp):
            os.remove(ruta_tmp)
        return f"Error: {str(e)}"

def actualizar_multiples_campos(dataset,archivo,id,valorID,nuevos_valores,delimitador=","):

    """Actualiza el valor de varias columnas para un registro específico identificado por 'id'.
    'id' es el nombre de la columna que identifica al registro a actualizar y 'valorID' es el valor de esa columna.
    'nuevos_valores' es un diccionario con el formato {columna:valor} donde columna es el nombre de la columna a actualizar y valor es el nuevo valor de esa columna.
    """

    ruta_in, ruta_out = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return "No se encontro el archivo ingresado"

    actualizado = False
    ruta_tmp = str(ruta_out) + '.tmp'

    taxonomia = ["family", "kingdom", "genus", "phylum", "scientificname", "higherClassification","order","class"]

    # Primero se lee el archivo original en busqueda del registro que se quiere modificar, verificando que existan el registro y la columna a modificar
    try:
        with open(ruta_in, 'r', encoding='utf-8') as archivo_in, \
             open(ruta_tmp, 'w', encoding='utf-8', newline='') as archivo_out:
            lector = csv.DictReader(archivo_in, delimiter=delimitador)
            campos = lector.fieldnames
        
            if not id in campos:
                return "La columna de identificación no existe"
            
            for col in nuevos_valores.keys():
                if col not in campos:
                    return f"La columna {col} no existe en el dataset" 

            escritor = csv.DictWriter(archivo_out, fieldnames=campos, delimiter=",")
            escritor.writeheader()

            for fila in lector:
                if str(fila[id]) == str(valorID):
                    # Iteramos sobre el diccionario para actualizar cada campo
                    fila_mod = fila.copy()
                    
                    for col, val in nuevos_valores.items():
                        fila_mod[col] = val
                    errores = []
                    
                    for col_mod, val in nuevos_valores.items():
                        col = col_mod.lower()
                        val_str = str(val).strip() if val is not None else ""
                        
                        if "latitude" in col:
                            try:
                                if validacion.verificar_rango(fila_mod[col_mod],90,-90):
                                    errores.append(f"Latitud {fila_mod[col_mod]} fuera de rango")
                            except ValueError:
                                errores.append("Latitud debe ser numerica")
                        elif "longitude" in col:
                            try:
                                if validacion.verificar_rango(fila_mod[col_mod],180,-180):
                                    errores.append(f"Longitud {fila_mod[col_mod]} fuera de rango")
                            except ValueError:
                                errores.append("Longitud debe ser numerica")
                    
                    lat = next((c for c in campos if "latitude" in c.lower()), None)
                    lon = next((c for c in campos if "longitude" in c.lower()), None)
                    if lat and lon:
                        tiene_lat = bool(fila_mod[lat] and str(fila_mod[lat].strip())) # La primera condicion es para evitar errores si el valor es None
                        tiene_lon = bool(fila_mod[lon] and str(fila_mod[lon].strip()))
                        if tiene_lat != tiene_lon:
                            errores.append("Error: Los cambios dejan una coordenada vacia y otra con valor")
                    
                    if errores:
                        raise ValueError(f"Errores encontrados: {', '.join(errores)}")
                    
                    fila = fila_mod
                    actualizado = True
                
                escritor.writerow(fila)

        if not actualizado:
            if os.path.exists(ruta_tmp):
                os.remove(ruta_tmp)
                logger.log_error(dataset,"UPDATE")
                return f"No se encontro el registro con el id {id}"
        
        # Si todo sale bien, el archivo temporal con las modificaciones reemplaza al original
        os.replace(ruta_tmp, ruta_out)
        logger.log(dataset, "UPDATE", 1)
        return "Columnas actualizadas exitosamente"
    
    except Exception as e:
        if os.path.exists(ruta_tmp):
            os.remove(ruta_tmp)
        return f"Error: {str(e)}"