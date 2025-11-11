#!/bin/bash

# Script para iniciar Django con OAuth auto-configurado
# Uso: ./runserver.sh [puerto]

set -e

PUERTO=${1:-8000}

echo "🚀 Iniciando servidor Django en puerto $PUERTO"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "📦 Activando entorno virtual..."
    source venv/bin/activate
fi

# Configurar OAuth automáticamente
echo "🔧 Configurando OAuth para puerto $PUERTO..."
python3 manage.py setup_oauth --puerto $PUERTO

# Ejecutar migraciones si es necesario
echo "📊 Verificando migraciones..."
python3 manage.py migrate --check > /dev/null 2>&1 || {
    echo "⚙️ Aplicando migraciones..."
    python3 manage.py migrate
}

# Iniciar servidor
echo "🌐 Iniciando servidor en http://localhost:$PUERTO"
echo "📝 OAuth configurado para:"
echo "   - http://localhost:$PUERTO/accounts/google/login/callback/"
echo "   - Presiona Ctrl+C para detener"
echo ""

python3 manage.py runserver localhost:$PUERTO