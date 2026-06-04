import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def obtener_media_inaturalist(id_observacion):
    """
    Dado un ID de observación, devuelve un DataFrame con la multimedia asociada.
    """
    df = pd.read_csv(BASE_DIR / 'raw_datasets' / 'inaturalist' / "media.csv", sep=',', encoding='utf-8', on_bad_lines='skip')
    return df[df["id"].astype(str) == str(id_observacion)] # Filtramos por la columna "id" que corresponde al ID de la observación en iNaturalist

def obtener_media_xeno(core_id):
    """
    Dado un CoreId de xeno-canto, devuelve un DataFrame con la multimedia asociada.
    """
    df = pd.read_csv(BASE_DIR / 'raw_datasets' / 'xeno-canto' / "Multimedia.txt", sep=',', encoding='utf-8', on_bad_lines='skip')
    return df[df["CoreId"].astype(str) == str(core_id)] # Filtramos por la columna "CoreId" que corresponde al ID de la grabación en xeno-canto