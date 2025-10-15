from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Carrito


@receiver(post_save, sender=User)
def crear_carrito_usuario(sender, instance, created, **kwargs):
    if created:
        Carrito.objects.create(user=instance)


@receiver(post_save, sender=User)
def guardar_carrito_usuario(sender, instance, **kwargs):
    if not hasattr(instance, 'carrito'):
        Carrito.objects.create(user=instance)