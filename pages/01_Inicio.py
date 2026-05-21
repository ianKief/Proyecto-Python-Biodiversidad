import streamlit as st


st.set_page_config(
    page_title="Inicio",
    page_icon="🌿",
)

# Titulo de la aplicacion
st.title("Portal de Biodiversidad")

# Proposito e importancia
st.header("Sobre la aplicación")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Propósito")
    st.write("""
             Esta aplicación tiene como objetivo proporcionar información detallada sobre la biodiversidad en diferentes regiones del mundo. 
             A través de datos actualizados y visualizaciones interactivas, los usuarios pueden explorar la riqueza de especies,
             su distribución geográfica y las amenazas que enfrentan.""")

with col2:
    st.subheader("Importancia")
    st.write("""
             La biodiversidad es fundamental para el equilibrio de los ecosistemas y el bienestar humano. 
             Proteger la biodiversidad es crucial para garantizar la sostenibilidad de nuestro planeta 
             y preservar los recursos naturales para las futuras generaciones.""")

st.divider()

# Estandar Darwin Core
st.header("Estandar Darwin Core (DwC)")
with st.expander("¿Qué es el estándar Darwin Core?"):
    st.write("""
             **¿Qué es?**
             Es un estándar de datos mantenido por la organizacion *Biodiversity Information Standards* (TDWG)
             basado en un conjunto de términos diseñados para facilitar el intercambio de información sobre biodiversidad.

             **¿Para qué sirve?**
             Se utiliza para crear un lenguaje común que permita a los investigadores, conservacionistas y otros interesados
             compartir datos de biodiversidad de manera eficiente y precisa.""")

st.divider()

# Instrucciones de uso
st.header("Instrucciones de uso")
st.info("Sigue estos pasos para navegar por la plataforma:")

st.markdown("""
1. **Navegación:** Utiliza el menú lateral para acceder a diferentes secciones de la aplicación.
2. **Consultas:** A través de esta plataforma, tendrás acceso a una amplia base de datos de biodiversidad, 
            donde podrás realizar consultas específicas sobre especies, regiones y amenazas.
""")