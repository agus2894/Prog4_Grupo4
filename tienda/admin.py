from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Producto, Pedido, PedidoItem

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("title", "marca", "price", "stock", "active", "created_at", "seller", "preview_image")
    list_filter = ("active", "marca", "created_at")
    search_fields = ("title", "description", "marca")
    fields = ("title", "description", "marca", "price", "stock", "image", "active", "seller")
    
    def preview_image(self, obj):
        """Muestra una preview de la imagen en el admin"""
        return format_html(
            '<img src="{}" style="max-width: 50px; max-height: 50px; object-fit: cover; border-radius: 4px;" />',
            obj.get_thumbnail_url()
        )
    preview_image.short_description = "Preview"


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
    actions = ['marcar_como_procesando', 'marcar_como_enviado', 'marcar_como_entregado', 'marcar_como_cancelado']
    
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
    
    def marcar_como_procesando(self, request, queryset):
        updated = 0
        for pedido in queryset:
            if pedido.estado != 'procesando':
                pedido.estado = 'procesando'
                pedido.save()
                
                # Enviar notificaciones
                from .views import enviar_email_pedido
                from telegram_bot.utils import enviar_pedido_telegram
                
                enviar_email_pedido(pedido, 'procesando', request)
                enviar_pedido_telegram(pedido.user, pedido, 'procesando')
                updated += 1
        
        self.message_user(request, f'{updated} pedidos marcados como "Procesando" y notificaciones enviadas. 📧🤖', messages.SUCCESS)
    marcar_como_procesando.short_description = "Marcar como Procesando"
    
    def marcar_como_enviado(self, request, queryset):
        updated = 0
        for pedido in queryset:
            if pedido.estado != 'enviado':
                pedido.estado = 'enviado'
                pedido.save()
                
                # Enviar notificaciones
                from .views import enviar_email_pedido
                from telegram_bot.utils import enviar_pedido_telegram
                
                enviar_email_pedido(pedido, 'enviado', request)
                enviar_pedido_telegram(pedido.user, pedido, 'enviado')
                updated += 1
        
        self.message_user(request, f'{updated} pedidos marcados como "Enviado" y notificaciones enviadas. 📧🤖', messages.SUCCESS)
    marcar_como_enviado.short_description = "Marcar como Enviado"
    
    def marcar_como_entregado(self, request, queryset):
        updated = 0
        for pedido in queryset:
            if pedido.estado != 'entregado':
                pedido.estado = 'entregado'
                pedido.save()
                
                # Enviar notificaciones
                from .views import enviar_email_pedido
                from telegram_bot.utils import enviar_pedido_telegram
                
                enviar_email_pedido(pedido, 'entregado', request)
                enviar_pedido_telegram(pedido.user, pedido, 'entregado')
                updated += 1
        
        self.message_user(request, f'{updated} pedidos marcados como "Entregado" y notificaciones enviadas. 📧🤖', messages.SUCCESS)
    marcar_como_entregado.short_description = "Marcar como Entregado"
    
    def marcar_como_cancelado(self, request, queryset):
        updated = 0
        for pedido in queryset:
            if pedido.estado != 'cancelado':
                pedido.estado = 'cancelado'
                pedido.save()
                
                # Enviar notificaciones
                from .views import enviar_email_pedido
                from telegram_bot.utils import enviar_pedido_telegram
                
                enviar_email_pedido(pedido, 'cancelado', request)
                enviar_pedido_telegram(pedido.user, pedido, 'cancelado')
                updated += 1
        
        self.message_user(request, f'{updated} pedidos marcados como "Cancelado" y notificaciones enviadas. 📧🤖', messages.SUCCESS)
    marcar_como_cancelado.short_description = "Marcar como Cancelado"
