from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
from django.contrib.auth.models import User
from .models import Profile


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adaptador personalizado para manejar la autenticación social
    """
    
    def save_user(self, request, sociallogin, form=None):
        """
        Guarda el usuario y crea automáticamente su perfil
        """
        user = super().save_user(request, sociallogin, form)
        
        # Obtener datos adicionales del proveedor social
        extra_data = sociallogin.account.extra_data
        
        # Crear o actualizar perfil
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Configurar datos del perfil según el proveedor
        if sociallogin.account.provider == 'google':
            if 'given_name' in extra_data:
                user.first_name = extra_data.get('given_name', '')
            if 'family_name' in extra_data:
                user.last_name = extra_data.get('family_name', '')
                
        elif sociallogin.account.provider == 'github':
            if 'name' in extra_data and extra_data['name']:
                name_parts = extra_data['name'].split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
            
            # GitHub puede proporcionar información de empresa
            if 'company' in extra_data and extra_data['company']:
                profile.empresa = extra_data['company']
        
        # Guardar cambios
        user.save()
        profile.save()
        
        return user
    
    def populate_user(self, request, sociallogin, data):
        """
        Llena los datos del usuario desde la información social
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Asegurar que el email esté configurado
        if not user.email and sociallogin.account.extra_data.get('email'):
            user.email = sociallogin.account.extra_data['email']
            
        return user