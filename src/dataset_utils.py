import pandas as pd
from src.columnas import obtener_columna_real

def detectar_separador(ruta):
    with open(ruta, encoding="utf-8") as f:
        primer_linea = f.readline()
        return "\t" if "\t" in primer_linea else ","

def cordenadas_validas(df):
    """
    Calcula el porcentaje de coordenadas válidas en un dataframe. 
    """
    col_lat = obtener_columna_real(df, 'Latitud')
    col_lon = obtener_columna_real(df, 'Longitud')

    if not col_lat or not col_lon or  len(df) == 0:
        return 0.0
    
    coords_validas = (
        pd.to_numeric(df[col_lat], errors="coerce").between(-90, 90) &
        pd.to_numeric(df[col_lon], errors="coerce").between(-180, 180)
    ).sum()

    return round(coords_validas / len(df) * 100, 2)

def fechas_validas(df):
    """
    Calcula el porcentaje de fechas válidas en un dataframe, buscando una columna que contenga "eventDate".
    """
    col_fecha = obtener_columna_real(df, 'Fecha de observación')
    if not col_fecha or len(df) == 0:
        return 0.0
    
    cantidad_validas = pd.to_datetime(df[col_fecha], errors="coerce").notna().sum()
    return round(cantidad_validas / len(df) * 100, 2)

def completitud_promedio(df):
    """Calcula el porcentaje promedio de valores no nulos por registro en un dataframe.
    """
    if len(df) == 0:
        return 0.0
    return  round(df.notna().mean().mean() * 100, 2)