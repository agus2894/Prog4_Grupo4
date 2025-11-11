#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def setup_oauth_if_needed():
    """
    Configura automáticamente OAuth según el entorno cuando se ejecuta runserver
    """
    if len(sys.argv) >= 2 and sys.argv[1] == 'runserver':
        try:
            # Solo intentar si Django está configurado
            import django
            from django.conf import settings
            django.setup()
            
            from django.contrib.sites.models import Site
            from allauth.socialaccount.models import SocialApp
            
            # Detectar entorno
            is_render = 'RENDER' in os.environ
            is_local = settings.DEBUG and not is_render
            
            if is_local:
                # Detectar puerto del comando runserver
                port = '8000'  # default
                if len(sys.argv) >= 3:
                    runserver_arg = sys.argv[2]
                    if ':' in runserver_arg:
                        port = runserver_arg.split(':')[1]
                expected_domain = f'localhost:{port}'
            else:
                render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
                expected_domain = render_host if render_host else 'mercadito-pesca.onrender.com'
            
            # Verificar si el site necesita actualización
            try:
                current_site = Site.objects.get(id=1)
                if current_site.domain != expected_domain:
                    current_site.domain = expected_domain
                    current_site.name = 'Local Development' if is_local else 'Mercadito Pesca - Producción'
                    current_site.save()
                    
                    # Asegurar asociación del provider
                    try:
                        google_app = SocialApp.objects.get(provider='google')
                        if current_site not in google_app.sites.all():
                            google_app.sites.add(current_site)
                    except SocialApp.DoesNotExist:
                        pass
                    
                    print(f"🔧 OAuth configurado automáticamente para: {expected_domain}")
            except Site.DoesNotExist:
                pass
                
        except Exception:
            # Si algo falla, continuar sin configurar
            pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Configurar OAuth automáticamente si es necesario
    setup_oauth_if_needed()
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
