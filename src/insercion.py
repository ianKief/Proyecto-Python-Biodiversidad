from lectura import listar_columnas

def crear_estructura_registro(dataset, archivo, delimitador="\t"):
    
    """ Retorna la lista de columnas del dataset excluyendo el ID. """
    
    columnas = listar_columnas(dataset, archivo, delimitador)
    if not columnas:
        return None
    return columnas[1:]
