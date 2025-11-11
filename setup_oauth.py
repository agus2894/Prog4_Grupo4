#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings

def setup_oauth_site():
    """
    Configura automáticamente el Site según el entorno
    """
    try:
        # Detectar si estamos en desarrollo local o en Render
        is_render = 'RENDER' in os.environ
        is_local = settings.DEBUG and not is_render
        
        if is_local:
            # Desarrollo local
            domain = 'localhost:8000'
            name = 'Local Development'
            print(f"🔧 Configurando para DESARROLLO LOCAL...")
        else:
            # Producción en Render
            render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
            if render_host:
                domain = render_host
                name = 'Mercadito Pesca - Producción'
            else:
                domain = 'mercadito-pesca.onrender.com'
                name = 'Mercadito Pesca - Producción'
            print(f"🚀 Configurando para PRODUCCIÓN...")
        
        # Obtener o crear el site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={'domain': domain, 'name': name}
        )
        
        # Actualizar si existe pero tiene valores diferentes
        if not created and (site.domain != domain or site.name != name):
            old_domain = site.domain
            site.domain = domain
            site.name = name
            site.save()
            print(f"✅ Site actualizado: {old_domain} → {domain}")
        else:
            print(f"✅ Site configurado: {domain}")
        
        # Asegurar que el provider de Google esté asociado al site correcto
        try:
            google_app = SocialApp.objects.get(provider='google')
            if site not in google_app.sites.all():
                google_app.sites.add(site)
                print(f"✅ Provider Google asociado al site {domain}")
            else:
                print(f"✅ Provider Google ya está asociado")
        except SocialApp.DoesNotExist:
            print("⚠️  Provider Google no encontrado - configurar en admin")
        
        print(f"\n🎉 Configuración OAuth lista para: {domain}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_oauth_site()