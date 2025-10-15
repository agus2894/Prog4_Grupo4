from django.contrib import admin
from django.utils.html import format_html
from .models import Producto, Pedido, PedidoItem

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("title", "marca", "price", "stock", "active", "image_preview", "created_at", "seller")
    list_filter = ("active", "marca", "created_at")
    search_fields = ("title", "description", "marca")
    fields = ("title", "description", "marca", "price", "stock", "image", "active", "seller")
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "Sin imagen"
    image_preview.short_description = "Vista previa"


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'fecha_pedido', 'estado_badge', 'total', 'items_count')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('user__username', 'user__email', 'direccion_envio')
    readonly_fields = ('fecha_pedido', 'fecha_actualizacion', 'total')
    fields = ('user', 'estado', 'total', 'direccion_envio', 'telefono', 'notas', 'fecha_pedido', 'fecha_actualizacion')
    inlines = [PedidoItemInline]
    
    def estado_badge(self, obj):
        colors = {
            'pendiente': '#6c757d',
            'procesando': '#ffc107',
            'enviado': '#17a2b8',
            'entregado': '#28a745',
            'cancelado': '#dc3545',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Cantidad de Items'
