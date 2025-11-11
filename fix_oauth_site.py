#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def fix_oauth_site():
    try:
        # Obtener el app de Google
        app = SocialApp.objects.get(provider='google')
        print(f"App encontrada: {app.name}")
        
        # Obtener el site actual
        site = Site.objects.get_current()
        print(f"Site actual: {site.domain}")
        
        # Limpiar sites anteriores y agregar solo el actual
        current_sites = list(app.sites.all())
        print(f"Sites actuales asociados: {[s.domain for s in current_sites]}")
        
        app.sites.clear()
        app.sites.add(site)
        
        # Verificar resultado
        final_sites = list(app.sites.all())
        print(f"Sites finales asociados: {[s.domain for s in final_sites]}")
        
        print("✅ OAuth site actualizado correctamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_oauth_site()