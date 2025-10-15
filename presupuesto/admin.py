from django.contrib import admin
from .models import Presupuesto, PresupuestoItem


class PresupuestoItemInline(admin.TabularInline):
    model = PresupuestoItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'fecha_creacion', 'estado', 'total')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('user__username', 'notas')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'total')
    inlines = [PresupuestoItemInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('user', 'estado', 'total')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
    )
