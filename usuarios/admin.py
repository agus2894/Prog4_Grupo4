from django.contrib import admin
from .models import Profile
from django.contrib.auth.models import User

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('user__username', 'user__email')
    list_editable = ('is_admin',)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'


class CustomUserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_admin')
    list_filter = ('is_staff', 'is_superuser', 'profile__is_admin')
    
    def get_is_admin(self, obj):
        return obj.profile.is_admin if hasattr(obj, 'profile') else False
    get_is_admin.short_description = 'Es Admin Tienda'
    get_is_admin.boolean = True


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
