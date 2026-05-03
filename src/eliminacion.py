import csv
import logger
from lectura import obtener_ruta


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
        reader=csv.DictWriter(actualizado,fieldnames=campos,delimiter=",")
        reader.writeheader()
        reader.writerows(registros)

    logger.log(dataset,"DELETE",cant)

    return "Se eliminaron los registros requeridos"

