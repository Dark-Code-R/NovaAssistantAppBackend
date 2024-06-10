# Usa la imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de requerimientos a la imagen
COPY requirements.txt requirements.txt

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación a la imagen
COPY . .

# Comando para ejecutar la aplicación usando Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
