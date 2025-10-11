from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False, help_text="Es administrador de la tienda")
    
    def __str__(self):
        return f"{self.user.username} ({'Admin' if self.is_admin else 'Comprador'})"
    
    def save(self, *args, **kwargs):
        # Sincronizar permisos de Django
        super().save(*args, **kwargs)
        if self.is_admin:
            self.user.is_staff = True
            self.user.is_superuser = True
        else:
            self.user.is_staff = False
            self.user.is_superuser = False
        # Evitar recursión infinita: usar update() en lugar de save()
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