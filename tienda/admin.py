from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("title", "marca", "price", "stock", "active", "created_at", "seller")
    list_filter = ("active", "marca", "created_at")
    search_fields = ("title", "description", "marca")
