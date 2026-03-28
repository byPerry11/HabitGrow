#!/bin/sh
set -e

# Cargar variables de entorno si existe .env en /app
if [ -f /app/.env.production ]; then
  export $(grep -v '^#' /app/.env.production | xargs)
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting process: $@"
exec "$@"
