from django.db import models
from django.contrib.auth.models import User
from tienda.models import Producto
from decimal import Decimal


class Presupuesto(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='presupuestos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True, help_text='Notas adicionales del presupuesto')
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
    
    def __str__(self):
        return f"Presupuesto #{self.id} - {self.user.username} - ${self.total}"
    
    def calcular_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total = total
        self.save()
        return total


class PresupuestoItem(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Item de Presupuesto'
        verbose_name_plural = 'Items de Presupuesto'
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        self.subtotal = Decimal(self.precio_unitario) * Decimal(self.cantidad)
        super().save(*args, **kwargs)
