#!/usr/bin/env bash

set -o errexit

echo "Iniciando deployment..."

# instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# migraciones
echo " Ejecutando migraciones..."
python manage.py migrate --noinput

# collectstatic
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Configurar datos iniciales (incluyendo superusuario)
echo "Configurando datos iniciales..."
python manage.py setup_database

echo "Deployment completado!"