from django.conf import settings
from django.db import models


class Producto(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="productos")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    marca = models.CharField(max_length=100, blank=True, default="Generico")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='productos/', blank=True, null=True, help_text="Imagen del producto")
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} (Stock: {self.stock})"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['price']),
            models.Index(fields=['active']),
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
