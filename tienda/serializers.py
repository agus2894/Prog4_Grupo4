from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ["id", "seller", "title", "description", "marca", "price", "stock", 
                 "image", "image_url", "created_at", "active"]
        
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
