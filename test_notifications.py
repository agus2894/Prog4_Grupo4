#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

def test_email():
    """Test email functionality"""
    print("=== PRUEBA DE EMAIL ===")
    
    try:
        # Verificar configuración
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        
        # Buscar un usuario para enviar email de prueba
        user = User.objects.first()
        if not user:
            print("❌ No hay usuarios en la base de datos")
            return
            
        print(f"Enviando email de prueba a: {user.email}")
        
        # Enviar email de prueba
        result = send_mail(
            subject='[Mercadito] Prueba de notificación',
            message=f'Hola {user.first_name or user.username}! Este es un email de prueba del sistema de notificaciones.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        if result:
            print("✅ Email enviado correctamente")
        else:
            print("❌ Error enviando email")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_telegram():
    """Test Telegram functionality"""
    print("\n=== PRUEBA DE TELEGRAM ===")
    
    try:
        # Verificar token
        token = settings.TELEGRAM_BOT_TOKEN
        print(f"TELEGRAM_BOT_TOKEN: {token[:20]}..." if token else "❌ No configurado")
        
        # Buscar usuario con Telegram vinculado
        from usuarios.models import Profile
        
        profiles_with_telegram = Profile.objects.exclude(telegram_chat_id__isnull=True).exclude(telegram_chat_id__exact='')
        
        if not profiles_with_telegram:
            print("❌ No hay usuarios con Telegram vinculado")
            print("💡 Vincular Telegram en: /telegram/vincular/")
            return
            
        profile = profiles_with_telegram.first()
        user = profile.user
        
        print(f"Enviando notificación de prueba a: {user.username}")
        print(f"Chat ID: {profile.telegram_chat_id}")
        
        # Crear pedido ficticio para prueba
        from tienda.models import Pedido, PedidoItem, Producto
        
        # Buscar un producto
        producto = Producto.objects.first()
        if not producto:
            print("❌ No hay productos para crear pedido de prueba")
            return
            
        # Intentar enviar notificación
        from telegram_bot.utils import enviar_pedido_telegram
        
        # Crear datos ficticios para la prueba
        from django.utils import timezone
        
        class MockPedido:
            id = 999
            total = 25.99
            fecha_pedido = timezone.now()
            estado = 'creado'
            direccion_envio = "Dirección de prueba"
            
            def get_estado_display(self):
                return "Creado"
                
            class items:
                @staticmethod
                def count():
                    return 1
                    
                @staticmethod
                def all():
                    class MockItem:
                        producto = producto
                        cantidad = 1
                        precio = 25.99
                    return [MockItem()]
        
        mock_pedido = MockPedido()
        
        result = enviar_pedido_telegram(user, mock_pedido, 'prueba')
        
        if result:
            print("✅ Notificación Telegram enviada")
        else:
            print("❌ Error enviando notificación Telegram")
            
    except Exception as e:
        print(f"❌ Error Telegram: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email()
    test_telegram()