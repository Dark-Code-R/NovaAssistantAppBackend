# Usa la imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de requisitos
COPY requirements.txt requirements.txt

# Instala las dependencias
RUN pip install -r requirements.txt

# Copia el resto de los archivos de la aplicación
COPY . .

# Especifica el comando para ejecutar la aplicación
CMD ["python", "app.py"]
