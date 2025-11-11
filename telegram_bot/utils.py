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
Utilidades para notificaciones de Telegram
"""
import asyncio
import threading
import logging
from io import BytesIO
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings

logger = logging.getLogger(__name__)

def enviar_presupuesto_telegram(user, presupuesto, pdf_buffer: BytesIO) -> bool:
    """
    Enviar presupuesto por Telegram de forma thread-safe
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("Token de Telegram no configurado")
        return False
        
    try:
        # Verificar si el usuario tiene Telegram vinculado
        if hasattr(user, 'profile') and user.profile.telegram_chat_id:
            chat_id = user.profile.telegram_chat_id
            
            def _enviar_async():
                """Función para ejecutar en thread separado"""
                try:
                    from .bot import MercaditoBot
                    
                    # Crear nuevo loop para este thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        mercadito_bot = MercaditoBot()
                        
                        # Inicializar bot
                        result = loop.run_until_complete(mercadito_bot.inicializar())
                        if not result:
                            logger.error("No se pudo inicializar el bot")
                            return False
                        
                        # Enviar presupuesto
                        result = loop.run_until_complete(
                            mercadito_bot.enviar_presupuesto(chat_id, presupuesto, pdf_buffer)
                        )
                        return result
                        
                    finally:
                        loop.close()
                        
                except Exception as e:
                    logger.error(f"Error en hilo de Telegram presupuesto: {e}")
                    return False
            
            # Ejecutar en thread pool
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_enviar_async)
                try:
                    result = future.result(timeout=30)  # Timeout de 30 segundos
                    logger.info(f"Notificación de presupuesto enviada a Telegram para usuario {user.username}")
                    return result if result else True  # Retorna True si no hay errores
                except Exception as e:
                    logger.error(f"Error ejecutando thread de Telegram: {e}")
                    return False
            
        else:
            logger.info(f"Usuario {user.username} no tiene Telegram vinculado")
            return False
            
    except Exception as e:
        logger.error(f"Error enviando presupuesto por Telegram: {e}")
        return False
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
    Enviar notificación de pedido por Telegram de forma thread-safe
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("Token de Telegram no configurado")
        return False
        
    try:
        # Verificar si el usuario tiene Telegram vinculado
        if hasattr(user, 'profile') and user.profile.telegram_chat_id:
            chat_id = user.profile.telegram_chat_id
            
            def _enviar_async():
                """Función para ejecutar en thread separado"""
                try:
                    from .bot import MercaditoBot
                    
                    # Crear nuevo loop para este thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        mercadito_bot = MercaditoBot()
                        
                        # Inicializar bot
                        result = loop.run_until_complete(mercadito_bot.inicializar())
                        if not result:
                            logger.error("No se pudo inicializar el bot")
                            return False
                        
                        # Enviar notificación
                        result = loop.run_until_complete(
                            mercadito_bot.enviar_pedido(chat_id, pedido, accion)
                        )
                        return result
                        
                    finally:
                        loop.close()
                        
                except Exception as e:
                    logger.error(f"Error en hilo de Telegram pedido: {e}")
                    return False
            
            # Ejecutar en thread pool
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_enviar_async)
                try:
                    result = future.result(timeout=30)  # Timeout de 30 segundos
                    logger.info(f"Notificación de pedido enviada a Telegram para usuario {user.username}")
                    return result if result else True  # Retorna True si no hay errores
                except Exception as e:
                    logger.error(f"Error ejecutando thread de Telegram: {e}")
                    return False
            
        else:
            logger.info(f"Usuario {user.username} no tiene Telegram vinculado")
            return False
            
    except Exception as e:
        logger.error(f"Error enviando pedido por Telegram: {e}")
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