from django.conf import settings
from django.db import models

class Producto(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="productos")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    marca = models.CharField(max_length=100, blank=True, default="Generico")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title and self.stock > 0
