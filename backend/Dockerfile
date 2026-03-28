FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y activar el buffer de salida para logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema para Postgres y Pillow (manejo de imágenes)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
        python3-dev \
        libjpeg-dev \
        zlib1g-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copiamos los requerimientos desde la carpeta backend
COPY backend/requirements.txt /app/requirements.txt

# Instalamos los requerimientos y dependencias de producción
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn whitenoise dj-database-url

# Copiamos todo el proyecto
COPY . /app

# Entrypoint para ejecutar migraciones y collectstatic antes de arrancar
COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Directorio de trabajo al backend (Django)
WORKDIR /app/backend

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "habitgrow.wsgi:application"]
