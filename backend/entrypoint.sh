#!/bin/sh
set -e

# Cargar variables de entorno si existe .env en /app
if [ -f /app/.env.production ]; then
  export $(grep -v '^#' /app/.env.production | xargs)
fi

# ── Fix: asegurar que las columnas de Google existen en la BD ──
# Usa IF NOT EXISTS para que sea idempotente (seguro de correr muchas veces)
echo "Ensuring Google auth columns exist..."
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    try:
        cursor.execute(\"ALTER TABLE users_profile ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE\")
        cursor.execute(\"ALTER TABLE users_profile ADD COLUMN IF NOT EXISTS google_avatar VARCHAR(200)\")
        print('Google auth columns OK')
    except Exception as e:
        print(f'Column check skipped: {e}')
"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting process: $@"
exec "$@"
