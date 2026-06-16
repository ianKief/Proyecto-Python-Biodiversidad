import csv
import os
from src import logger
from src.lectura import obtener_ruta
from src import validacion
from dateutil import parser

def identificador(dataset,archivo,valorID,delimitador=","):

    """Funcion que recibe en valorID el ID a eliminar"""

    rute_in,rute_out=obtener_ruta(dataset,archivo)
    with open(rute_in,"r",encoding="utf-8") as archivo:
        datos=csv.DictReader(archivo,delimiter=delimitador)
        campos=datos.fieldnames
        campoID=campos[0]
        registros=[]
        cant=0
        for fila in datos:
            if(fila[campoID] is None or fila[campoID].strip()==""):
                continue
            else:
                if (fila[campoID]==valorID):
                    cant+=1
                else:
                    registros.append(fila)

    if cant==0:
        logger.log_error(dataset,"DELETE")
        return (f"ERROR, no se encontro un registro con ID: {valorID}")
    
    #Si se encontro el ID a eliminar guarda el archivo actualizado
    with open(rute_out,"w", encoding="utf-8") as actualizado:
        writer=csv.DictWriter(actualizado,fieldnames=campos,delimiter=",")
        writer.writeheader()
        writer.writerows(registros)

    logger.log(dataset,"DELETE",cant)

    return "Se eliminaron los registros requeridos"


def eliminar_columna(dataset,archivo,columna,valores,delimitador=","):

    """Funcion que recibe la columna a actualizar y en valores esta una lista con los valores que hay que eliminar de esa columna"""

    rute_in,rute_out=obtener_ruta(dataset,archivo)
    cant=0
    # Creamos un archivo temporal para escribir los registros que no se eliminaran, y luego reemplazamos el original con el temporal
    ruta_tmp = str(rute_out) + '.tmp'

    try:
        with open(rute_in, "r",encoding="utf-8") as archivo_in, \
            open(ruta_tmp, "w", encoding="utf-8", newline='') as archivo_out:
            datos=csv.DictReader(archivo_in, delimiter=delimitador)
            campos=datos.fieldnames
            
            if not (columna in campos):
                logger.log_error(dataset,"DELETE")
                return(f"La columna: {columna} no existe")
            
            writer=csv.DictWriter(archivo_out, fieldnames=campos, delimiter=",")
            writer.writeheader()
            
            for fila in datos:
                if str(fila[columna]) in valores:
                    cant+=1
                else:
                    writer.writerow(fila)
        
        if cant==0:
            if os.path.exists(ruta_tmp):
                os.remove(ruta_tmp)
            logger.log_error(dataset,"DELETE")
            return (f"No habia registros con los valores:{valores}")
        
        #Si se elimino algun registro se guarda el archivo actualizado con los registros eliminados
        os.replace(ruta_tmp, rute_out)
        logger.log(dataset,"DELETE",cant)
        return "Se eliminaron los registros requeridos"
    
    except Exception as e:
        if os.path.exists(ruta_tmp):
            os.remove(ruta_tmp)
        logger.log_error(dataset,"DELETE")
        return f"Hubo un error: {e}"


def condicion(dataset,archivo,columnas,valor,condicion,delimitador=","):

    """Funcion que recibe una lista de columnas a verificar, la condicion a cumplir y el valor por parametros,
       y elimina los registros que cumplan la condicion"""

    rute_in,rute_out=obtener_ruta(dataset,archivo)

    condiciones={
        "Igual":lambda a, b: a == b,
        "Diferente":lambda a, b: a!=b,
        "Mayor":lambda a, b: a > b,
        "Mayor o igual":lambda a, b: a >= b,
        "Menor":lambda a, b: a < b,
        "Menor o igual":lambda a, b: a <= b
    }

    if not(condicion in condiciones):
            return (f" la condicion {condicion} no es valida")
    
    cant = 0
    ruta_tmp = str(rute_out) + '.tmp'

    try:
        with open(rute_in,"r",encoding="utf-8") as archivo_in, \
            open(ruta_tmp,"w",encoding="utf-8", newline='') as archivo_out:
            datos=csv.DictReader(archivo_in,delimiter=delimitador)
            campos=datos.fieldnames

            writer=csv.DictWriter(archivo_out,fieldnames=campos,delimiter=",")
            writer.writeheader()

            for fila in datos:
                eliminar=False

                for columna in columnas:
                    dato=fila.get(columna)

                    if(dato is None or str(dato).strip()==''):
                        continue
                    
                    try:
                        dato_C=float(dato)
                        valor_C=float(valor)
                    except ValueError:
                        try:
                            dato_C=parser.parse(str(dato))
                            valor_C=parser.parse(str(valor))
                        except ValueError:
                                dato_C = str(dato).strip()
                                valor_C = str(valor).strip()
                        
                    if condiciones[condicion](dato_C,valor_C):
                        eliminar=True
                        break
                
                if eliminar:
                    cant+=1
                else:
                    writer.writerow(fila)
            
        if(cant==0):
            return "Ningun registro cumplia la condicion"
        os.replace(ruta_tmp, rute_out)
        logger.log(dataset,"DELETE",cant)
        return "Se eliminaron los registros que cumplian la condicion"
    
    except Exception as e:
        if os.path.exists(ruta_tmp):
            os.remove(ruta_tmp)
        logger.log_error(dataset,"DELETE")
        return f"Hubo un error: {e}"

def sanitizar(dataset,archivo,delimitador=","):
    """
    Funcion que utiliza las validaciones del modulo de validacion para eliminar datos conflictivos.
    Elimina los registros correspondientes y genera un nuevo archivo en processed_datasets.
    """

    ruta_in,ruta_out=obtener_ruta(dataset,archivo)
    if not ruta_in:
        return "No se encontro el archivo ingresado"

    invalidos = {}

    with open(ruta_in,"r",encoding="utf-8") as archivo_in:
        lector = csv.DictReader(archivo_in,delimiter=delimitador)
        campos = lector.fieldnames
        campo_id = campos[0] # Se asume que el primer campo es el ID

    # Defino una funcion auxiliar para agregar los IDs de los registros invalidos a un diccionario, junto con el motivo de la invalidacion
    def agregar_invalido(filas_inv, motivo):
        if filas_inv:
            for fila in filas_inv:
                id = fila[campo_id]
                if id not in invalidos:
                    invalidos[id] = []
                if motivo not in invalidos[id]:
                    invalidos[id].append(motivo)

    """Aqui se realizan todas las validaciones utilizando el modulo de validacion"""
    # 1. Validacion de ids duplicados
    duplicados = validacion.duplicados(dataset,archivo,delimitador)
    if duplicados:
        for id in duplicados:
            if id not in invalidos:
                invalidos[id] = []
            if "ID duplicado" not in invalidos[id]:
                invalidos[id].append("ID duplicado")
        
    # 2. Validacion de coordenadas
    coordenadas_invalidas = validacion.coordenadas(dataset,archivo,delimitador)
    if coordenadas_invalidas and coordenadas_invalidas[0]:
        agregar_invalido(coordenadas_invalidas[0], "Coordenadas fuera de rango")
        
    # 3. Validacion de inconsistencias
    inconsistentes = validacion.existe(dataset,archivo,delimitador)
    if inconsistentes:
        agregar_invalido(inconsistentes, "Inconsistencia encontrada (falta latitud o longitud)")

    # 4. Validacion de maximos y minimos
    fuera_rango = validacion.max_min(dataset,archivo,delimitador)
    if fuera_rango:
        agregar_invalido(fuera_rango, "Valor fuera de rango")

    # 5. Validacion de incertidumbre
    incertidumbre = validacion.incertidumbre(dataset,archivo,delimitador)
    if incertidumbre:
        agregar_invalido(incertidumbre.get("no_numeros", []), "No es un número")
        agregar_invalido(incertidumbre.get("negativos", []), "Valor negativo")
        agregar_invalido(incertidumbre.get("muy_alto", []), "Valor muy alto")
        
    # 6. Validacion de codigo de pais
    paises = validacion.country(dataset,archivo,delimitador)
    if paises:
        agregar_invalido(paises, "Código de país inválido")

    # 7. Validacion de fechas
    fecha=validacion.fechas(dataset,archivo,delimitador)
    if fecha:
        agregar_invalido(fecha, "Fecha invalida")

    registros_invalidos = 0
    registros_totales = 0
    with open(ruta_in,"r",encoding="utf-8") as archivo_in \
        , open(ruta_out,"w",encoding="utf-8") as archivo_out:
        lector = csv.DictReader(archivo_in,delimiter=delimitador)
        escritor = csv.DictWriter(archivo_out, fieldnames=campos, delimiter=delimitador)
        escritor.writeheader()
        for fila in lector:
            id = fila[campo_id]
            registros_totales += 1
            # Verifico que el ID del registro no este en el set de invalidos, si lo esta se omite su escritura y se cuenta como registro eliminado
            if id in invalidos:
                registros_invalidos += 1
                continue
            escritor.writerow(fila)
    
    if registros_invalidos == 0:
        return "No se encontraron registros conflictivos"
    elif registros_totales == 0:
        return "El dataset no contiene registros"
    else:
        porcentaje = ((registros_invalidos / registros_totales) * 100)
        logger.log(dataset,"DELETE",registros_invalidos)
        return f"Se eliminaron {registros_invalidos} registros conflictivos de un total de {registros_totales},lo que representa un {porcentaje:.2f}% del dataset"
        