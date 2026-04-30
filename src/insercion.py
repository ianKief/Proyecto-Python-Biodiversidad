from lectura import listar_columnas
from validacion import verificar_rango
import uuid

def crear_estructura_registro(dataset, archivo, delimitador="\t"):
    
    """ Retorna la lista de columnas del dataset excluyendo el ID. """
    
    columnas = listar_columnas(dataset, archivo, delimitador)
    if not columnas:
        return None
    return columnas[1:]

def generar_registro_vacio(columnas):

    """Genera un registro vacío con todas las columnas en None."""
    
    return {col: None for col in columnas}

def validar_registro(registro):

    """ Valida un registro individual antes de insertarlo en el dataset. Reutiliza verificar_rango() del módulo de validación (ejercicio 3)"""

    errores = []

    # Detectar automáticamente nombres de latitud/longitud
    columnas = registro.keys()

    latitud = [col for col in columnas if "latitude" in col.lower()]
    longitud = [col for col in columnas if "longitude" in col.lower()]

    campo_lat = latitud[0] if latitud else None
    campo_lon = longitud[0] if longitud else None

    valor_lat = registro.get(campo_lat, "") if campo_lat else ""
    valor_lon = registro.get(campo_lon, "") if campo_lon else ""

    # Reutiliza verificar_rango
    if campo_lat and verificar_rango(valor_lat, 90, -90):
        errores.append("Latitud inválida")

    if campo_lon and verificar_rango(valor_lon, 180, -180):
        errores.append("Longitud inválida")

    # Reutiliza lógica existe (3.B)
    if valor_lat.strip() != "" and valor_lon.strip() == "":
        errores.append("Existe latitud pero falta longitud")

    if valor_lon.strip() != "" and valor_lat.strip() == "":
        errores.append("Existe longitud pero falta latitud")

    # Reutiliza incertidumbre (3.F)
    if "coordinateUncertaintyInMeters" in registro:
        incertidumbre = registro["coordinateUncertaintyInMeters"]

        if incertidumbre is not None and incertidumbre.strip() != "":
            try:
                valor = float(incertidumbre)

                if valor < 0:
                    errores.append(
                        "coordinateUncertaintyInMeters negativo"
                    )

                elif valor > 1000:
                    errores.append(
                        "coordinateUncertaintyInMeters muy alto"
                    )

            except ValueError:
                errores.append(
                    "coordinateUncertaintyInMeters no numérico"
                )

    return len(errores) == 0, errores

def preparar_registro_para_csv(registro, estructura_4A):
    """
    Convierte el registro en una lista lista para escribir en el CSV.
    Genera el ID automáticamente.
    """
    fila = []
    nuevo_id = str(uuid.uuid4())
    fila.append(nuevo_id)

    for col in estructura_4A:
        valor = registro.get(col)
        fila.append("" if valor is None else valor)

    return fila
