from .lectura import listar_columnas, obtener_ruta
from .validacion import verificar_rango
import csv


def crear_estructura_registro(dataset, archivo, delimitador=","):
    
    """ Retorna la lista de columnas del dataset excluyendo el ID. """
    
    columnas = listar_columnas(dataset, archivo, delimitador)
    if not columnas:
        return None
    return columnas[1:]

def generar_registro_vacio(columnas):

    """Genera un registro vacío con todas las columnas en None."""
    
    return {col: None for col in columnas}

def validar_registro(registro):
    """
    Valida un registro individual antes de insertarlo en el dataset.
    Reutiliza verificar_rango() del módulo de validación (ejercicio 3).
    """
    errores = []

    columnas = registro.keys()

    paises_sudamerica = {"AR", "BO", "BR", "CL", "CO", "EC", "GY", "PY", "PE", "SR", "UY", "VE"}
    country = registro.get("countryCode", "") or ""

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

    # Reutiliza lógica existe
    if valor_lat.strip() != "" and valor_lon.strip() == "":
        errores.append("Existe latitud pero falta longitud")
    if valor_lon.strip() != "" and valor_lat.strip() == "":
        errores.append("Existe longitud pero falta latitud")

    # Reutiliza lógica max_min para Sudamérica
    if country in paises_sudamerica:
        if campo_lat and verificar_rango(valor_lat, 70, -70):
            errores.append("Latitud fuera del rango de Sudamérica")
        if campo_lon and verificar_rango(valor_lon, 160, -160):
            errores.append("Longitud fuera del rango de Sudamérica")

    # Reutiliza logica incertidumbre
    if "coordinateUncertaintyInMeters" in registro:
        incertidumbre = registro["coordinateUncertaintyInMeters"]
        if incertidumbre is not None and incertidumbre.strip() != "":
            try:
                valor = float(incertidumbre)
                if valor < 0:
                    errores.append("coordinateUncertaintyInMeters negativo")
                elif valor > 1000:
                    errores.append("coordinateUncertaintyInMeters muy alto")
            except ValueError:
                errores.append("coordinateUncertaintyInMeters no numérico")

    # Reutiliza logica de countryCode
    if "countryCode" in registro and not no_existe_dato(registro["countryCode"]):
        if pycountry.countries.get(alpha_2=country) is None:
            errores.append("Codigo de pais no reconocido")


    return len(errores) == 0, errores

def generar_id(dataset, archivo, delimitador):
    """
    Deduce cómo se construyen los IDs del dataset y genera el siguiente.
    Busca el ID máximo existente y le suma 1.
    Para Xeno-canto agrega el sufijo @XC.
    """
    ruta_in, ruta_out = obtener_ruta(dataset, archivo)
    ruta = ruta_out if ruta_out.exists() else ruta_in

    max_id = 0
    ultimo_id = ""

    with open(ruta, encoding="utf-8") as f:
        lector = csv.reader(f, delimiter=delimitador)
        next(lector)
        for fila in lector:
            if not fila:
                continue
            ultimo_id = fila[0].strip()
            try:
                numero = int(ultimo_id.replace("@XC", ""))
                if numero > max_id:
                    max_id = numero
            except ValueError:
                continue
    return ultimo_id, max_id + 1

def preparar_registro_para_csv(registro, estructura_4A, id, delimitador=","):
    """
    Convierte el registro en una lista lista para escribir en el CSV.
    Genera el ID automáticamente.
    """
    fila = []
    fila.append(id)

    for col in estructura_4A:
        valor = registro.get(col)
        fila.append("" if valor is None else valor)

    return fila

def insertar_registro(dataset, archivo, delimitador=","):
    """
    Lee el dataset, pide un registro por teclado, lo valida e inserta en processed_datasets/.
    """
    # 1. rutas
    ruta_in, ruta_out = obtener_ruta(dataset, archivo)
    if not ruta_in:
        return

    # 2. estructura de registro (4.A)
    estructura = crear_estructura_registro(dataset, archivo, delimitador)

    # 3. registro vacío (4.B)
    registro = generar_registro_vacio(estructura)

    print("\n=== Ingreso de datos ===")
    for col in estructura:
        valor = input(f"{col}: ")
        valor = valor.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        registro[col] = valor.strip()

    # 4. validar registro (4.C)
    es_valido, errores = validar_registro(registro)
    if not es_valido:
        print("\n⚠ El registro tiene errores y NO fue insertado:")
        for error in errores:
            print(f"  - {error}")
        return False

    # 5. preparar fila (4.D)
    id_formato, id_nuevo = generar_id(dataset, archivo, delimitador)
    if "@XC" in id_formato:
        id_nuevo = str(f"{id_nuevo}@XC")
    nueva_fila = preparar_registro_para_csv(registro, estructura, id_nuevo, delimitador)

    # 6. leer dataset original
    if ruta_out.exists():
        with open(ruta_out, encoding="utf-8") as f:
            lector = list(csv.reader(f, delimiter=delimitador))
    else:
        with open(ruta_in, encoding="utf-8") as f:
            lector = list(csv.reader(f, delimiter=delimitador))

    # 7. escribir nuevo archivo
    ruta_out.parent.mkdir(parents=True, exist_ok=True)

    with open(ruta_out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=delimitador)
        writer.writerows(lector)
        writer.writerow(nueva_fila)

    print(f"\n✔ Registro insertado en: {ruta_out}")
    return True

def insertar_multiples_registros(dataset, archivo, delimitador=","):
    """
    Ejercicio 4.G
    Extiende 4.F permitiendo ingresar múltiples registros
    en una sola ejecución.

    Lee dataset original o procesado, permite ingresar varios
    registros por teclado, valida cada uno y agrega solo los válidos.
    """

    # 1. rutas
    ruta_in, ruta_out = obtener_ruta(dataset, archivo)
    if not ruta_in:
        return False

    # 2. estructura (4.A)
    estructura = crear_estructura_registro(dataset, archivo, delimitador)

    # 3. leer archivo base
    if ruta_out.exists():
        with open(ruta_out, encoding="utf-8") as f:
            lector = list(csv.reader(f, delimiter=delimitador))
    else:
        with open(ruta_in, encoding="utf-8") as f:
            lector = list(csv.reader(f, delimiter=delimitador))

    # 4. lista de nuevos registros válidos
    nuevos_registros = []

    print("\n=== Inserción múltiple de registros ===")

    while True:

        # registro vacío (4.B)
        registro = generar_registro_vacio(estructura)

        print("\n--- Nuevo registro ---")

        # ingreso por teclado
        for col in estructura:
            valor = input(f"{col}: ")
            valor = valor.replace("\n", " ").replace("\r", " ").replace("\t", " ")
            registro[col] = valor.strip()

        # validar (4.C)
        es_valido, errores = validar_registro(registro)

        if es_valido:
            id_formato, id_nuevo = generar_id(dataset, archivo, delimitador) 
            id_nuevo += int(len(nuevos_registros))
            if "@XC" in id_formato:
                id_nuevo= str(f"{id_nuevo}@XC")
            nuevos_registros.append(preparar_registro_para_csv(registro, estructura, id_nuevo, delimitador))
            print("✔ Registro válido agregado a la operación.")
        else:
            print("\n⚠ Registro inválido. NO fue agregado:")
            for error in errores:
                print(f"  - {error}")

        # continuar o terminar
        continuar = input(
            "\n¿Desea ingresar otro registro? (s/n): "
        ).strip().lower()

        if continuar != "s":
            break

    # 5. escribir archivo final
    ruta_out.parent.mkdir(parents=True, exist_ok=True)

    with open(ruta_out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=delimitador)

        # datos previos
        writer.writerows(lector)

        # nuevos registros
        writer.writerows(nuevos_registros)

    print(
        f"\n✔ Se insertaron {len(nuevos_registros)} registros en: {ruta_out}"
    )

    return True
    