"""
Comando Django para configurar OAuth automáticamente
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

class Command(BaseCommand):
    help = 'Configura OAuth para Google automáticamente según el entorno'

    def add_arguments(self, parser):
        parser.add_argument(
            '--puerto',
            type=str,
            default='8000',
            help='Puerto para desarrollo local (por defecto: 8000)'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔧 Configurando OAuth automáticamente...")
        
        # Detectar entorno
        is_production = 'RENDER' in os.environ
        puerto = options['puerto']
        
        # Obtener credenciales
        google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
        google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        
        if not google_client_id or not google_client_secret:
            self.stdout.write(
                self.style.ERROR("❌ Faltan credenciales de Google en variables de entorno")
            )
            return
        
        try:
            # Configurar sitio
            site = Site.objects.get(id=1)
            
            if is_production:
                render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "mercadito-pesca.onrender.com")
                site.domain = render_host
                site.name = f"Mercadito Pesca - {render_host}"
                self.stdout.write(f"🌐 Configurando para PRODUCCIÓN: {render_host}")
            else:
                site.domain = f"localhost:{puerto}"
                site.name = f"Desarrollo Local ({puerto})"
                self.stdout.write(f"💻 Configurando para DESARROLLO: localhost:{puerto}")
            
            site.save()
            
            # Limpiar aplicaciones OAuth existentes
            SocialApp.objects.filter(provider='google').delete()
            
            # Crear nueva aplicación
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google OAuth' if is_production else 'Google OAuth Local',
                client_id=google_client_id,
                secret=google_client_secret,
            )
            google_app.sites.add(site)
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ OAuth configurado exitosamente para {site.domain}")
            )
            
            if is_production:
                self.stdout.write(
                    self.style.WARNING(
                        f"🔧 Verifica en Google Console: https://{site.domain}/accounts/google/login/callback/"
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error configurando OAuth: {e}")
            )