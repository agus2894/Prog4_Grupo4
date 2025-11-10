from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os


class Command(BaseCommand):
    help = 'Limpia aplicaciones OAuth duplicadas y las reconfigura'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Limpiando aplicaciones OAuth duplicadas...')
        
        # Mostrar aplicaciones actuales
        apps = SocialApp.objects.all()
        self.stdout.write(f'Aplicaciones encontradas: {apps.count()}')
        
        for app in apps:
            self.stdout.write(f'  - {app.provider}: {app.name} (ID: {app.id})')
        
        # Eliminar TODAS las aplicaciones sociales
        deleted_count, _ = SocialApp.objects.all().delete()
        self.stdout.write(f'🗑️  {deleted_count} aplicaciones eliminadas')
        
        # Configurar sitio correcto
        site = Site.objects.get_current()
        render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
        
        if render_hostname:
            site.domain = render_hostname
            site.name = 'Mercadito Producción'
        else:
            site.domain = 'localhost:8000'
            site.name = 'Mercadito Local'
        
        site.save()
        self.stdout.write(f'🌐 Sitio configurado: {site.domain}')
        
        # Recrear aplicaciones OAuth desde variables de entorno
        google_client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
        github_client_id = os.getenv('GITHUB_CLIENT_ID', '').strip()
        github_client_secret = os.getenv('GITHUB_CLIENT_SECRET', '').strip()
        
        # Crear Google OAuth
        if google_client_id and google_client_secret:
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=google_client_id,
                secret=google_client_secret,
            )
            google_app.sites.add(site)
            self.stdout.write('✅ Google OAuth recreado')
        else:
            self.stdout.write('⚠️  Google OAuth no configurado')
        
        # Crear GitHub OAuth
        if github_client_id and github_client_secret:
            github_app = SocialApp.objects.create(
                provider='github',
                name='GitHub',
                client_id=github_client_id,
                secret=github_client_secret,
            )
            github_app.sites.add(site)
            self.stdout.write('✅ GitHub OAuth recreado')
        else:
            self.stdout.write('⚠️  GitHub OAuth no configurado')
        
        # Verificar resultado
        final_apps = SocialApp.objects.all()
        self.stdout.write(f'\\n📋 Aplicaciones finales: {final_apps.count()}')
        for app in final_apps:
            self.stdout.write(f'  ✅ {app.provider}: {app.name}')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 OAuth limpiado y reconfigurado correctamente!')
        )