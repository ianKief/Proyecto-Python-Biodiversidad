from lectura import listar_columnas

def crear_estructura_registro(dataset, archivo, delimitador="\t"):
    
    """ Retorna la lista de columnas del dataset excluyendo el ID. """
    
    columnas = listar_columnas(dataset, archivo, delimitador)
    if not columnas:
        return None
    return columnas[1:]

def generar_registro_vacio(columnas):

    """Genera un registro vacío con todas las columnas en None."""
    
    return {col: None for col in columnas}

