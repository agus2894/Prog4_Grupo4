from django.contrib import admin
from django.utils.html import format_html
from .models import Producto

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
