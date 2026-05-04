import csv
import logger
from lectura import obtener_ruta

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
    with open(rute_in, "r",encoding="utf-8"):
        cant=0
        datos=csv.DictReader(archivo,delimiter=delimitador)
        registros=[]
        campos=datos.fieldnames
        if not (columna in datos.fieldnames):
            logger.log_error(dataset,"DELETE")
            return(f"La columna: {columna} no existe")
        else:
            for fila in datos:
                if (fila[columna] in valores):
                    cant+=1
                else:
                    registros.append(fila[columna])
    if cant==0:
        return (f"No habia registros con los valores:{valores}")
    
    #Si se elimino algun registro se guarda el archivo actualizado con los registros eliminados
    with open(rute_out,"w",encoding="utf-8") as actualizado:
        writer=csv.DictWriter(actualizado,fieldnames=campos,delimiter=",")
        writer.writeheader()
        writer.writerows(registros)

    logger.log(dataset,"DELETE",cant)

    return "Se eliminaron los registros requeridos"


def condicion(dataset,archivo,columnas,valor,condicion,delimitador=","):

    """Funcion que recibe una lista de columnas a verificar, la condicion a cumplir y el valor por parametros,
       y elimina los registros que cumplan la condicion"""

    rute_in,rute_out=obtener_ruta(dataset,archivo)
    cant=0
    registros=[]

    condiciones={
        "==":lambda a, b: a == b,
        "!=":lambda a, b: a!=b,
        ">":lambda a, b: a > b,
        ">=":lambda a, b: a >= b,
        "<":lambda a, b: a < b,
        "<=":lambda a, b: a <= b
    }

    with open(rute_in,"r",encoding="utf-8") as archivo_in:
        datos=csv.DictReader(archivo_in,delimiter=delimitador)
        campos=datos.fieldnames

        if not(condicion in condiciones):
            return (f" la condicion {condicion} no es valida")
        
        for columna in columnas:
            if not(columna in datos.fieldnames):
                print(f"El campo {columna} no existe")
                continue
            
            for fila in datos:
                dato=fila.get(columna)
                if(dato is None or dato.strip()==" "):
                    continue
                
                dato=float(dato)
                if (condiciones[condicion](dato,valor)):
                    cant+=1
                elif not(fila in registros):
                    registros.append(fila)
        
    if(cant==0):
        return "Ningun registro cumplia la condicion"
    
    with open(rute_out,"w",encoding="utf-8") as actualizado:
        writer=csv.DictWriter(actualizado,fieldnames=campos,delimiter=",")
        writer.writeheader()
        writer.writerows(registros)

    logger.log(dataset,"DELETE",cant)

    return "Se eliminaron los registros que cumplian la condicion"

