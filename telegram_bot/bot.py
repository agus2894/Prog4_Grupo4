"""
Bot de Telegram para Mercadito
Maneja notificaciones de presupuestos y pedidos
"""

import asyncio
import logging
from io import BytesIO
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from django.conf import settings
from django.contrib.auth.models import User
from usuarios.models import Profile

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class MercaditoBot:
    def __init__(self):
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start del bot"""
        chat_id = update.effective_chat.id
        user_name = update.effective_user.first_name
        
        welcome_message = f"""
🛒 ¡Hola {user_name}! Bienvenido a **Mercadito Bot**

Soy tu asistente personal para recibir notificaciones sobre:
• 📋 Presupuestos (con PDF adjunto)
• 📦 Estados de pedidos
• 🛍️ Ofertas especiales

**Para empezar:**
Usa el comando /vincular para conectar tu cuenta de usuario

**Comandos disponibles:**
/help - Ver ayuda
/vincular - Vincular tu cuenta
/estado - Ver tu estado de vinculación
/test - Probar notificaciones

¿Necesitas ayuda? Usa /help 👍
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help del bot"""
        help_text = """
🤖 **Ayuda de Mercadito Bot**

**Comandos principales:**
• `/start` - Iniciar el bot
• `/help` - Mostrar esta ayuda
• `/vincular` - Vincular tu cuenta de usuario
• `/estado` - Ver estado de vinculación
• `/test` - Probar notificaciones

**¿Cómo vincular mi cuenta?**
1. Usa `/vincular`
2. Te daré un código único
3. Ingresa el código en tu perfil web
4. ¡Listo! Recibirás notificaciones automáticas

**¿Qué notificaciones recibo?**
• 📋 Presupuestos generados (con PDF)
• 📦 Cambios en estado de pedidos
• 🎉 Ofertas y promociones

**Soporte:** Si tienes problemas, contacta al administrador de la tienda.
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def vincular_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /vincular para conectar cuenta de usuario"""
        chat_id = str(update.effective_chat.id)
        
        # Verificar si ya está vinculado
        try:
            profile = Profile.objects.get(telegram_chat_id=chat_id)
            message = f"""
✅ **Ya estás vinculado!**

Tu cuenta: `{profile.user.username}`
Email: `{profile.user.email}`
Tipo: {'👑 Administrador' if profile.is_admin else '🛍️ Cliente'}

Ya recibes notificaciones automáticas de:
• Presupuestos con PDF
• Estados de pedidos
• Ofertas especiales
            """
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            return
            
        except Profile.DoesNotExist:
            pass
        
        # Generar código de vinculación
        codigo_vinculacion = f"TG{chat_id[-6:]}"
        
        keyboard = [
            [InlineKeyboardButton("🌐 Ir al sitio web", url="http://localhost:8000/")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
🔗 **Vincular tu cuenta**

Para recibir notificaciones, necesitas vincular tu cuenta:

**Tu código de vinculación:** `{codigo_vinculacion}`

**Pasos:**
1. Ve a tu perfil en el sitio web
2. Ingresa el código: `{codigo_vinculacion}`
3. Guarda los cambios
4. ¡Listo! Recibirás notificaciones aquí

Tu Chat ID: `{chat_id}`

*Nota: Solo puedes vincular una cuenta por chat*
        """
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def estado_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /estado para ver estado de vinculación"""
        chat_id = str(update.effective_chat.id)
        
        try:
            profile = Profile.objects.get(telegram_chat_id=chat_id)
            
            message = f"""
📊 **Estado de tu cuenta**

✅ **Cuenta vinculada correctamente**

**Detalles:**
• Usuario: `{profile.user.username}`
• Email: `{profile.user.email}`
• Nombre: `{profile.user.get_full_name() or 'No especificado'}`
• Tipo: {'👑 Administrador' if profile.is_admin else '🛍️ Cliente'}
• Chat ID: `{chat_id}`

**Notificaciones activas:**
• 📋 Presupuestos con PDF ✅
• 📦 Estados de pedidos ✅
• 🎉 Ofertas especiales ✅

¡Todo funcionando correctamente! 🎊
            """
            
        except Profile.DoesNotExist:
            message = f"""
❌ **Cuenta no vinculada**

Tu chat no está conectado a ninguna cuenta.

**Para vincular:**
1. Usa el comando `/vincular`
2. Sigue las instrucciones

Chat ID: `{chat_id}`
            """
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /test para probar notificaciones"""
        chat_id = str(update.effective_chat.id)
        
        try:
            profile = Profile.objects.get(telegram_chat_id=chat_id)
            
            test_message = f"""
🧪 **Mensaje de Prueba**

¡Hola {profile.user.get_full_name() or profile.user.username}!

Esta es una notificación de prueba de Mercadito Bot.

✅ Tu bot está funcionando correctamente
✅ Las notificaciones están activas
✅ Recibirás avisos de presupuestos y pedidos

¡Sistema listo! 🚀
            """
            
            await update.message.reply_text(test_message, parse_mode=ParseMode.MARKDOWN)
            
        except Profile.DoesNotExist:
            await update.message.reply_text(
                "❌ Primero debes vincular tu cuenta con `/vincular`",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar comandos desconocidos"""
        message = """
❓ **Comando no reconocido**

Comandos disponibles:
• `/start` - Iniciar bot
• `/help` - Ayuda
• `/vincular` - Vincular cuenta
• `/estado` - Ver estado
• `/test` - Probar notificaciones

Usa `/help` para más información.
        """
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    def setup_handlers(self):
        """Configurar manejadores de comandos"""
        if not self.application:
            return
            
        # Comandos principales
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("vincular", self.vincular_command))
        self.application.add_handler(CommandHandler("estado", self.estado_command))
        self.application.add_handler(CommandHandler("test", self.test_command))
        
        # Manejar mensajes desconocidos
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.unknown_command))
    
    async def enviar_presupuesto(self, chat_id: str, presupuesto, pdf_buffer: BytesIO):
        """Enviar notificación de presupuesto con PDF"""
        try:
            if not self.application:
                return False
                
            message = f"""
📋 **¡Nuevo Presupuesto Generado!**

**Presupuesto #{presupuesto.id}**
💰 Total: $**{presupuesto.total}**
📅 Fecha: {presupuesto.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
📦 Items: {presupuesto.items.count()} productos

Estado: {presupuesto.get_estado_display()}

📎 **PDF adjunto** ⬇️
            """
            
            # Enviar mensaje
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Enviar PDF
            pdf_buffer.seek(0)
            await self.application.bot.send_document(
                chat_id=chat_id,
                document=pdf_buffer,
                filename=f"presupuesto_{presupuesto.id}.pdf",
                caption=f"📄 Presupuesto #{presupuesto.id} - ${presupuesto.total}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando presupuesto por Telegram: {e}")
            return False
    
    async def enviar_pedido(self, chat_id: str, pedido, accion: str):
        """Enviar notificación de pedido"""
        try:
            if not self.application:
                return False
            
            # Configurar mensajes según la acción
            emojis = {
                'creado': '🎉',
                'procesando': '⚙️',
                'enviado': '🚚',
                'entregado': '✅',
                'cancelado': '❌'
            }
            
            titulos = {
                'creado': '¡Pedido Confirmado!',
                'procesando': 'Pedido en Preparación',
                'enviado': '¡Pedido Enviado!',
                'entregado': '¡Pedido Entregado!',
                'cancelado': 'Pedido Cancelado'
            }
            
            emoji = emojis.get(accion, '📦')
            titulo = titulos.get(accion, 'Actualización de Pedido')
            
            message = f"""
{emoji} **{titulo}**

**Pedido #{pedido.id}**
💰 Total: $**{pedido.total}**
📅 Fecha: {pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M')}
📦 Items: {pedido.items.count()} productos
📍 Estado: **{pedido.get_estado_display()}**

{self._get_mensaje_estado(accion)}
            """
            
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando notificación de pedido: {e}")
            return False
    
    def _get_mensaje_estado(self, accion: str) -> str:
        """Obtener mensaje específico según el estado"""
        mensajes = {
            'creado': '¡Gracias por tu compra! Pronto comenzaremos a preparar tu pedido.',
            'procesando': '⚙️ Tu pedido está siendo preparado en nuestro almacén.',
            'enviado': '🚚 Tu pedido está en camino. ¡Esperamos que lo recibas pronto!',
            'entregado': '🎊 ¡Disfruta tus productos! Si tienes algún problema, contáctanos.',
            'cancelado': '😔 Lamentamos que se haya cancelado. Contáctanos si tienes dudas.'
        }
        return mensajes.get(accion, '')
    
    async def inicializar(self):
        """Inicializar la aplicación del bot"""
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("Token de Telegram no configurado")
            return False
            
        try:
            self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            self.setup_handlers()
            
            # Inicializar en modo de prueba (no polling continuo)
            logger.info("Bot de Telegram inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando bot de Telegram: {e}")
            return False


# Instancia global del bot
mercadito_bot = MercaditoBot()