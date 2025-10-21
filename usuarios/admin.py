from django.contrib import admin
from .models import Profile
from django.contrib.auth.models import User

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_admin', 'telegram_chat_id', 'telefono', 'empresa')
    list_filter = ('is_admin',)
    search_fields = ('user__username', 'user__email', 'telefono', 'empresa')
    list_editable = ('is_admin',)
    fields = ('user', 'is_admin', 'telegram_chat_id', 'telefono', 'empresa', 'direccion', 'role')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('is_admin', 'telegram_chat_id', 'telefono', 'empresa', 'direccion', 'role')


class CustomUserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'get_is_admin', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'profile__is_admin', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('is_active', 'is_staff')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Información de Usuario', {
            'fields': ('username', 'password', 'email', 'first_name', 'last_name')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    def get_is_admin(self, obj):
        return obj.profile.is_admin if hasattr(obj, 'profile') else False
    get_is_admin.short_description = 'Admin Tienda'
    get_is_admin.boolean = True


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
