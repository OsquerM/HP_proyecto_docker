#slim es la versión ligera, ocupa menos espacio y tiene todo lo necesario para python
FROM python:3.11-slim

#Establece /app como carpeta de trabajo dentro del contenedor. Todos los comandos siguientes se ejecutan desde ahí.
WORKDIR /app
#Copia solo el requirements.txt desde el pc al contenedor y así aprovechamos la caché de docker
COPY requirements.txt .
#Instala todas las librerías listadas en requirements.txt. --no-cache-dir no guarda caché de pip para reducir el tamaño de la imagen.
RUN pip install --no-cache-dir -r requirements.txt
#Copia todo el proyecto del pc al contenedor. El primer . es tu carpeta local y el segundo . es /app dentro del contenedor.
COPY . .

#Añade /app al path de Python para que encuentre los módulos correctamente. Sin esto los imports como from app.database import... darían error.
ENV PYTHONPATH=/app
#Indica el puerto que vamos a usar
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# uvicorn → servidor web para FastAPI
# app.main:app → busca el objeto app en /app/app/main.py
# --host 0.0.0.0 → acepta conexiones desde cualquier IP
# --port 8000 → escucha en el puerto 8000
# --reload → reinicia automáticamente cuando detecta cambios en el código