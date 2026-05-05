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

### 4.2 Streamlit

```bash
streamlit run app.py
```

Se abrira un host local en el navegador con la pagina desarrollada en el proyecto.

### 4.3 Pycountry

```bash
pip install pycountry

pip install python-dateutil
```

Esto se necesita para que funcione el modulo de Validacion