FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y activar el buffer de salida para logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema para Postgres y Pillow (manejo de imágenes)
RUN apt-get update && apt-get install -y 
    libpq-dev 
    gcc 
    python3-dev 
    libjpeg-dev 
    zlib1g-dev 
    && rm -rf /var/lib/apt/lists/*

# Copiamos los requerimientos desde la carpeta backend
COPY backend/requirements.txt .

# Instalamos los requerimientos y aseguramos las dependencias de producción
RUN pip install --no-cache-dir -r requirements.txt 
    && pip install --no-cache-dir gunicorn whitenoise dj-database-url

# Copiamos todo el proyecto
COPY . .

# Cambiamos el directorio de trabajo a la carpeta del backend para Django
WORKDIR /app/backend

# Comando para ejecutar migraciones, recolectar archivos estáticos e iniciar Gunicorn
CMD python manage.py migrate && 
    python manage.py collectstatic --noinput && 
    gunicorn --bind 0.0.0.0:8000 habitgrow.wsgi:application
