# Usar una imagen base de Python
FROM python:3.8-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt al contenedor
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de archivos al contenedor
COPY . .

# Exponer el puerto en el que se ejecutará la aplicación Streamlit
EXPOSE 8501

# Iniciar la aplicación Streamlit
CMD ["streamlit", "run", "app.py"]