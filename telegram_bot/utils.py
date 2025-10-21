"""
Funciones utilitarias para el bot de Telegram
"""

import asyncio
import threading
from io import BytesIO
from typing import Optional
from asgiref.sync import sync_to_async

from .bot import mercadito_bot


def enviar_presupuesto_telegram(user, presupuesto, pdf_buffer: BytesIO) -> bool:
    """
    Envía un presupuesto por Telegram si el usuario tiene chat_id configurado
    """
    try:
        if not hasattr(user, 'profile') or not user.profile.telegram_chat_id:
            return False
        
        chat_id = user.profile.telegram_chat_id
        
        # Ejecutar en un hilo separado para evitar conflictos con event loops
        def run_telegram_task():
            try:
                # Crear nuevo event loop en el hilo
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Inicializar bot si no está listo
                    if not mercadito_bot.application:
                        result = loop.run_until_complete(mercadito_bot.inicializar())
                        if not result:
                            return False
                    
                    # Enviar presupuesto
                    result = loop.run_until_complete(
                        mercadito_bot.enviar_presupuesto(chat_id, presupuesto, pdf_buffer)
                    )
                    return result
                    
                finally:
                    loop.close()
                    
            except Exception as e:
                print(f"Error en hilo de Telegram: {e}")
                return False
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=run_telegram_task)
        thread.start()
        thread.join(timeout=10)  # Timeout de 10 segundos
        
        return True  # Asumimos éxito si no hay excepciones
            
    except Exception as e:
        print(f"Error enviando presupuesto por Telegram: {e}")
        return False


def enviar_pedido_telegram(user, pedido, accion: str) -> bool:
    """
    Envía una notificación de pedido por Telegram
    """
    try:
        if not hasattr(user, 'profile') or not user.profile.telegram_chat_id:
            return False
        
        chat_id = user.profile.telegram_chat_id
        
        # Ejecutar en un hilo separado para evitar conflictos con event loops
        def run_telegram_task():
            try:
                # Crear nuevo event loop en el hilo
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Inicializar bot si no está listo
                    if not mercadito_bot.application:
                        result = loop.run_until_complete(mercadito_bot.inicializar())
                        if not result:
                            return False
                    
                    # Enviar notificación
                    result = loop.run_until_complete(
                        mercadito_bot.enviar_pedido(chat_id, pedido, accion)
                    )
                    return result
                    
                finally:
                    loop.close()
                    
            except Exception as e:
                print(f"Error en hilo de Telegram: {e}")
                return False
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=run_telegram_task)
        thread.start()
        thread.join(timeout=10)  # Timeout de 10 segundos
        
        return True  # Asumimos éxito si no hay excepciones
            
    except Exception as e:
        print(f"Error enviando pedido por Telegram: {e}")
        return False


def verificar_chat_vinculado(chat_id: str) -> Optional[str]:
    """
    Verifica si un chat_id está vinculado a algún usuario
    Retorna el username si está vinculado, None si no
    """
    try:
        from usuarios.models import Profile
        profile = Profile.objects.get(telegram_chat_id=chat_id)
        return profile.user.username
    except Profile.DoesNotExist:
        return None


def vincular_usuario_telegram(username: str, chat_id: str) -> bool:
    """
    Vincula un usuario con un chat_id de Telegram
    """
    try:
        from django.contrib.auth.models import User
        user = User.objects.get(username=username)
        user.profile.telegram_chat_id = chat_id
        user.profile.save()
        return True
    except Exception:
        return False