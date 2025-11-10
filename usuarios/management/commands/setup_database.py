from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from usuarios.models import Profile
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
            return

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

            # Verificar usuarios creados
            usuarios = User.objects.filter(is_superuser=True)
            self.stdout.write('👥 Superusuarios disponibles:')
            for user in usuarios:
                profile_status = "✅ Admin" if hasattr(user, 'profile') and user.profile.is_admin else "❌ Sin perfil admin"
                self.stdout.write(f'   • {user.username} ({user.email}) - {profile_status}')

            self.stdout.write(
                self.style.SUCCESS('🎉 Configuración completada exitosamente!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la configuración: {str(e)}')
            )