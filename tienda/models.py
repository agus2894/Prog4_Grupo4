from django.conf import settings
from django.db import models
import hashlib


class Producto(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="productos")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    marca = models.CharField(max_length=100, blank=True, default="Generico")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField()
    image = models.URLField(blank=True, null=True, help_text="URL de la imagen del producto")
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def get_image_url(self):
        """Retorna la imagen del producto o una imagen placeholder automática"""
        if self.image:
            return self.image
        
        # Generar imagen placeholder inteligente basada en el producto
        title_lower = self.title.lower()
        
        # Detectar categorías específicas de equipamiento de pesca
        if any(word in title_lower for word in ['caña', 'rod', 'vara', 'telescópica']):
            category = 'fishing+rod'
        elif any(word in title_lower for word in ['reel', 'carrete', 'frontal', 'rotativo']):
            category = 'fishing+reel'  
        elif any(word in title_lower for word in ['anzuelo', 'hook', 'círculo', 'j-hook']):
            category = 'fishing+hook'
        elif any(word in title_lower for word in ['carnada', 'señuelo', 'artificial', 'spinner', 'cuchara']):
            category = 'fishing+lure'
        elif any(word in title_lower for word in ['plomada', 'peso', 'sinker', 'pirámide']):
            category = 'fishing+weight'
        elif any(word in title_lower for word in ['línea', 'nylon', 'monofilamento', 'multifilamento']):
            category = 'fishing+line'
        elif any(word in title_lower for word in ['caja', 'organizadora', 'tackle+box']):
            category = 'tackle+box'
        elif any(word in title_lower for word in ['silla', 'chair', 'asiento']):
            category = 'fishing+chair'
        elif any(word in title_lower for word in ['red', 'net', 'landing']):
            category = 'fishing+net'
        elif any(word in title_lower for word in ['lombriz', 'carnada+viva', 'gusano']):
            category = 'fishing+bait'
        else:
            category = 'fishing+equipment'  # Equipamiento genérico de pesca
        
        # Usar un seed basado en el ID para consistencia
        seed = f"{category}-{self.id}" if hasattr(self, 'id') and self.id else category
        
        # Unsplash con fallback a Picsum si falla
        return f"https://source.unsplash.com/400x300/?{category}"
    
    def get_thumbnail_url(self):
        """Retorna una versión thumbnail de la imagen"""
        if self.image:
            return self.image
        
        # Misma lógica para equipamiento de pesca en thumbnail
        title_lower = self.title.lower()
        
        if any(word in title_lower for word in ['caña', 'rod', 'vara', 'telescópica']):
            category = 'fishing+rod'
        elif any(word in title_lower for word in ['reel', 'carrete', 'frontal', 'rotativo']):
            category = 'fishing+reel'  
        elif any(word in title_lower for word in ['anzuelo', 'hook', 'círculo', 'j-hook']):
            category = 'fishing+hook'
        elif any(word in title_lower for word in ['carnada', 'señuelo', 'artificial', 'spinner', 'cuchara']):
            category = 'fishing+lure'
        elif any(word in title_lower for word in ['plomada', 'peso', 'sinker', 'pirámide']):
            category = 'fishing+weight'
        elif any(word in title_lower for word in ['línea', 'nylon', 'monofilamento', 'multifilamento']):
            category = 'fishing+line'
        elif any(word in title_lower for word in ['caja', 'organizadora', 'tackle+box']):
            category = 'tackle+box'
        elif any(word in title_lower for word in ['silla', 'chair', 'asiento']):
            category = 'fishing+chair'
        elif any(word in title_lower for word in ['red', 'net', 'landing']):
            category = 'fishing+net'
        elif any(word in title_lower for word in ['lombriz', 'carnada+viva', 'gusano']):
            category = 'fishing+bait'
        else:
            category = 'fishing+equipment'
        
        return f"https://source.unsplash.com/200x150/?{category}"

    def __str__(self):
        return f"{self.title} (Stock: {self.stock})"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['price']),
            models.Index(fields=['active']),
            models.Index(fields=['marca']),
            models.Index(fields=['stock']),
            models.Index(fields=['active', 'stock']),  # Índice compuesto para consultas frecuentes
            models.Index(fields=['seller', 'active']),  # Para dashboard de vendedor
        ]


class Carrito(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carrito")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.user.username}"

    @property
    def total_items(self):
        return sum(item.cantidad for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    def add_item(self, producto, cantidad=1):
        """Agregar o actualizar un producto en el carrito"""
        item, created = CarritoItem.objects.get_or_create(
            carrito=self,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        if not created:
            item.cantidad += cantidad
            item.save()
        return item

    def remove_item(self, producto):
        """Eliminar un producto del carrito"""
        try:
            item = self.items.get(producto=producto)
            item.delete()
        except CarritoItem.DoesNotExist:
            pass

    def clear(self):
        """Vaciar el carrito"""
        self.items.all().delete()


class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('carrito', 'producto')

    def __str__(self):
        return f"{self.cantidad}x {self.producto.title}"

    @property
    def subtotal(self):
        return self.cantidad * self.producto.price

    def clean(self):
        """Validar que no se agreguen más productos que el stock disponible"""
        if self.cantidad > self.producto.stock:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"Solo hay {self.producto.stock} unidades disponibles de {self.producto.title}")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pedidos")
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    direccion_envio = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    notas = models.TextField(blank=True)
    
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.user.username} - {self.estado}"
    
    class Meta:
        ordering = ['-fecha_pedido']
        indexes = [
            models.Index(fields=['user', '-fecha_pedido']),
            models.Index(fields=['estado']),
        ]


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.title} (Pedido #{self.pedido.id})"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
