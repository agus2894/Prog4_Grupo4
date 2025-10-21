from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False, help_text="Es administrador de la tienda")
    direccion = models.CharField(max_length=255, blank=True, null=True)
    empresa = models.CharField(max_length=100, blank=True, null=True)
    fecha_verificacion = models.DateTimeField(blank=True, null=True)
    role = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    telegram_chat_id = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        unique=True,
        help_text="ID del chat de Telegram para notificaciones"
    )
    
    def __str__(self):
        telegram_status = "📱 Telegram" if self.telegram_chat_id else "❌ Sin Telegram"
        return f"{self.user.username} ({'Admin' if self.is_admin else 'Comprador'}) - {telegram_status}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_admin:
            self.user.is_staff = True
            self.user.is_superuser = True
        else:
            self.user.is_staff = False
            self.user.is_superuser = False
        User.objects.filter(pk=self.user.pk).update(
            is_staff=self.user.is_staff,
            is_superuser=self.user.is_superuser
        )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)