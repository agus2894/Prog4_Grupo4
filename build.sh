#!/usr/bin/env bash

set -o errexit

# instalar dependencias (Render hace pip install automáticamente si lo especificás en build)
# pip install -r requirements.txt  # Comentado porque Render lo hace automáticamente

# migraciones
python manage.py migrate --noinput

# collectstatic
python manage.py collectstatic --noinput