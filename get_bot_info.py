#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

import asyncio
from telegram_bot.bot import MercaditoBot
from django.conf import settings

async def get_bot_info():
    """Obtener información del bot"""
    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ Token no configurado")
        return
        
    bot = MercaditoBot()
    await bot.inicializar()
    
    if bot.application:
        bot_info = await bot.application.bot.get_me()
        print(f"🤖 Bot: @{bot_info.username}")
        print(f"📝 Nombre: {bot_info.first_name}")
        print(f"🆔 ID: {bot_info.id}")
        print(f"\n📱 Para vincular Telegram:")
        print(f"1. Buscar @{bot_info.username} en Telegram")
        print(f"2. Enviar /start")
        print(f"3. Enviar /vincular")
        print(f"4. Usar el código en: http://localhost:8000/telegram/vincular/")

if __name__ == "__main__":
    asyncio.run(get_bot_info())