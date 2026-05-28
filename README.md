# Instalacion de dependencias y ejecucion:

## 1. Crear entorno virtual

```bash
python -m venv venv
```

## 2. Activar entorno virtual

En Windows:
```powershell
.\venv\Scripts\Activate
```

En Linux/macOS:
```bash
source venv/bin/activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Ejecutar herramientas

### 4.1 Jupyter

```bash
jupyter notebook
```
Se abrira un host local en el navegador con el directorio del proyecto, se debe ingresar a la carpeta **notebooks** y ejecutar el que desee.

*Los datasets que desee probar deben estar subidos en la carpeta **raw_datasets**, de lo contrario el notebook no funcionará.*
*Además, por convención, las carpetas de los datasets deben renombrarse a **iadiza**, **inaturalist** y **xeno-canto** para su correcto funcionamiento en cada notebook*

### 4.2 Streamlit

```bash
streamlit run app.py
```

Se abrira un host local en el navegador con la pagina desarrollada en el proyecto.

### 4.3 Pycountry y dateutil

```bash
pip install pycountry

pip install python-dateutil
```

Esto se necesita para que funcione el modulo de Validacion

# Documentación general

## 1. Campos de relevancia

Se define a continuación una lista de campos que son considerados relevantes a la hora de la búsqueda, análisis y muestra de información

- ID
- Nombre científico
- Nombre del organismo
- Observador
- Fecha de observación
- Habitat
- Continente
- País
- Provincia o estado
- Latitud
- Longitud
- Reino
- Clase
- Familia
- Género
- Sexo