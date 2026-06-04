# Diccionario con los conceptos y sus posibles nombres de columna en los datasets.
columnas = {
    'ID': ['id', 'gbifID'],
    'Nombre científico': ['scientificName'],
    'Nombre del organismo': ['organismName'],
    'Observador': ['recordedBy'],
    'Fecha de observación': ['eventDate'],
    'Habitat': ['habitat'],
    'Continente': ['continent'],
    'País': ['country', 'countryCode'],
    'Provincia': ['stateProvince'],
    'Latitud': ['decimalLatitude', 'latitudeDecimal'],
    'Longitud': ['decimalLongitude', 'longitudeDecimal'],
    'Reino': ['kingdom'],
    'Clase': ['class'],
    'Familia': ['family'],
    'Género': ['genus'],
    'Sexo': ['sex']
}

def obtener_columna_real(df, concepto):
    """
    Busca en el DataFrame cual es el nombre real de la columna 
    basandose en el diccionario de columnas. Retorna el nombre original o None.
    """
    if concepto not in columnas:
        return None
        
    # Creamos un diccionario para mapear la version en minuscula al nombre original
    cols_df_lower = {col.lower(): col for col in df.columns}
    
    # Buscamos cada alias en nuestras columnas
    for alias in columnas[concepto]:
        if alias.lower() in cols_df_lower:
            return cols_df_lower[alias.lower()] # Retornamos el nombre exacto como esta en el CSV
            
    return None # Si no encontro ninguno de los sinónimos