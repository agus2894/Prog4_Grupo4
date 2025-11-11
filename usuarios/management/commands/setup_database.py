from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from usuarios.models import Profile
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os


class Command(BaseCommand):
    help = 'Inicializa la base de datos con datos por defecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la carga de datos incluso si ya existen usuarios',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando configuración de la base de datos...')
        
        # Verificar si ya hay usuarios
        if User.objects.exists() and not options['force']:
            self.stdout.write(
                self.style.WARNING('⚠️  Ya existen usuarios en la base de datos.')
            )
            self.stdout.write('Use --force para sobrescribir los datos existentes.')
        else:
            try:
                # Cargar datos desde el fixture
                fixture_path = 'datos_iniciales.json'
                if os.path.exists(fixture_path):
                    self.stdout.write('📂 Cargando datos iniciales...')
                    call_command('loaddata', fixture_path)
                    self.stdout.write(
                        self.style.SUCCESS('✅ Datos iniciales cargados correctamente')
                    )
                else:
                    # Crear superusuario manualmente si no existe el fixture
                    self.stdout.write('👤 Creando superusuario por defecto...')
                    
                    if not User.objects.filter(username='admin').exists():
                        admin_user = User.objects.create_superuser(
                            username='admin',
                            email='admin@mercadito.com',
                            password='admin123',
                            first_name='Administrador',
                            last_name='Sistema'
                        )
                        
                        # Asegurar que tiene el perfil correcto
                        profile, created = Profile.objects.get_or_create(user=admin_user)
                        profile.is_admin = True
                        profile.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS('✅ Superusuario creado: admin/admin123')
                        )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error cargando datos: {str(e)}')
                )

        # Configurar aplicaciones sociales OAuth - REMOVIDO
        # Ahora se maneja con el comando fix_oauth para evitar duplicados
        self.stdout.write('🔐 OAuth se configura con comando fix_oauth')

        # Verificar usuarios creados
        usuarios = User.objects.filter(is_superuser=True)
        self.stdout.write('👥 Superusuarios disponibles:')
        for user in usuarios:
            profile_status = "✅ Admin" if hasattr(user, 'profile') and user.profile.is_admin else "❌ Sin perfil admin"
            self.stdout.write(f'   • {user.username} ({user.email}) - {profile_status}')

        self.stdout.write(
            self.style.SUCCESS('🎉 Configuración completada exitosamente!')
        )

    def setup_oauth(self):
        """Configura la aplicación OAuth de Google"""
        # Obtener variables de entorno
        google_client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()

        # Obtener sitio y configurar dominio correcto
        site = Site.objects.get_current()
        
        # Configurar dominio según el entorno
        render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
        if render_hostname:
            # Estamos en Render (producción)
            site.domain = render_hostname
            site.name = 'Mercadito Producción'
        else:
            # Estamos en desarrollo local
            site.domain = 'localhost:8000'
            site.name = 'Mercadito Local'
        
        site.save()
        self.stdout.write(f'   🌐 Sitio configurado: {site.domain}')

        # Limpiar aplicaciones existentes para evitar duplicados
        SocialApp.objects.filter(provider='google').delete()

        # Configurar Google OAuth
        if google_client_id and google_client_secret:
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=google_client_id,
                secret=google_client_secret,
            )
            google_app.sites.add(site)
            self.stdout.write('   ✅ Google OAuth configurado')
        else:
            self.stdout.write('   ⚠️  Google OAuth no configurado (faltan variables de entorno)')