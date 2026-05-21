import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Datasets",
    page_icon="📂"
)
st.title("Datasets disponibles")

directorio = Path(__file__).parent.parent / "processed_datasets"

datos = []
for archivo in directorio.glob("*.csv"):
    stat = archivo.stat()
    datos.append({
        "Nombre": archivo.name,
        "Tamaño (MB)": round(stat.st_size / (1024 * 1024), 4),
        "Última modificación": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    })

if datos:
    st.dataframe(datos, use_container_width=True, hide_index=True)
else:
    st.warning("No hay datasets disponibles en processed_datasets/")
