from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = Producto
        fields = ["id", "seller", "seller_name", "title", "description", "marca", 
                 "price", "stock", "image", "image_url", "created_at", "active"]
        read_only_fields = ["seller", "created_at"]  # Campos de solo lectura
        
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
