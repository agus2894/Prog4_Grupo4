from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = Producto
        fields = ["id", "seller", "seller_name", "title", "description", "marca", 
                 "price", "stock", "created_at", "active"]
        read_only_fields = ["seller", "created_at"]  # Campos de solo lectura
