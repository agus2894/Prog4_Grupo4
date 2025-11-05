#!/usr/bin/env bash

set -o errexit

# instalar dependencias
pip install -r requirements.txt

# migraciones
python manage.py migrate --noinput

# collectstatic
python manage.py collectstatic --noinput