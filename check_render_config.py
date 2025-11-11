#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.conf import settings

def verificar_configuracion_render():
    """
    Verificar la configuración específica para Render
    """
    print("=== CONFIGURACIÓN RENDER ===")
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"RENDER detectado: {'RENDER' in os.environ}")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    
    if 'RENDER' in os.environ:
        print("✅ Configuración para PRODUCCIÓN (Render)")
        print("  - Emails: Console backend (no SMTP)")
        print("  - Telegram: Funcional (si está vinculado)")
    else:
        print("✅ Configuración para DESARROLLO")
        print("  - Emails: SMTP real")
        print("  - Telegram: Funcional (si está vinculado)")
    
    print("\n=== VARIABLES DE ENTORNO ===")
    print(f"DATABASE_URL configurado: {'DATABASE_URL' in os.environ}")
    print(f"SECRET_KEY configurado: {'SECRET_KEY' in os.environ}")
    print(f"GOOGLE_CLIENT_ID configurado: {'GOOGLE_CLIENT_ID' in os.environ}")
    print(f"TELEGRAM_BOT_TOKEN configurado: {'TELEGRAM_BOT_TOKEN' in os.environ}")

if __name__ == "__main__":
    verificar_configuracion_render()