#!/usr/bin/env bash

set -o errexit

echo "🚀 Iniciando deployment..."

# instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --noinput

# collectstatic
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Limpiar OAuth duplicados (CRÍTICO para evitar error 500)
echo "🧹 Limpiando OAuth duplicados..."
python manage.py fix_oauth

# Configurar datos iniciales (incluyendo superusuario)
echo "👤 Configurando datos iniciales..."
python manage.py setup_database

echo "✅ Deployment completado!"