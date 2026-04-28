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

def actualizar_registro(dataset,archivo,id,valorID,columna,valor,delimitador=","):

    """Actualiza el valor de una columna para un registro específico identificado por 'id'.
    'id' es el valor de la columna que identifica al registro a actualizar.
    'columna' es el nombre de la columna a actualizar y 'valor' es el nuevo valor que se asignará a esa columna.
    """

    ruta_in, ruta_out = obtener_ruta(dataset,archivo)
    if not ruta_in:
        return "No se encontro el archivo ingresado"

    actualizado = False
    registros_actualizados = []

    # Primero se lee el archivo original en busqueda del registro que se quiere modificar, verificando que existan el registro y la columna a modificar
    with open(ruta_in, 'r', encoding='utf-8') as archivo_in:
        lector = csv.DictReader(archivo_in, delimiter=delimitador)
        campos = lector.fieldnames
        if not id in campos:
                return "La columna de identificación no existe"
        if not columna in campos:
                return "La columna a actualizar no existe"
        for fila in lector:
            if fila[id] == valorID:
                fila[columna] = valor
                actualizado = True
            registros_actualizados.append(fila)
    if not actualizado:
        return "No se encontro el registro con el id ingresado"
    
    # Si se encontro el registro, se escribe el nuevo archivo procesado con la modificacion realizada
    with open(ruta_out, 'w', encoding='utf-8', newline='') as archivo_out:
        escritor = csv.DictWriter(archivo_out, fieldnames=campos, delimiter=",")
        escritor.writeheader()
        escritor.writerows(registros_actualizados)
    return "Columna actualizada exitosamente"