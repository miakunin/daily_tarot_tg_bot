# -*- coding: utf-8 -*-
"""
Обработчик текстовых сообщений
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..config import Config

logger = logging.getLogger(__name__)

class MessageHandlers:
    """Обработчик текстовых сообщений"""
    
    def __init__(self, config: Config):
        """Инициализация обработчика"""
        self.config = config
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик обычных текстовых сообщений"""
        user = update.effective_user
        user_name = user.first_name or "друг"
        message_text = update.message.text
        
        try:
            # Определить статус AI для показа в сообщении
            status = self.config.get_status_info()
            ai_status = "🤖 AI" if status['ai_enabled'] else "📚 классические"
            
            # Базовое сообщение с инструкциями
            help_message = f"""
🔮 Привет, {user_name}! Я ваш бот Ежедневных Предсказаний Таро.

**Основные команды:**
✨ /fortune - получить своё ежедневное предсказание
📊 /stats - посмотреть вашу статистику
🎴 /deck - узнать о колоде карт

**AI и настройки:**
🤖 /ai - переключить режим толкований
🔧 /status - проверить статус AI системы

**Помощь:**
❓ /help - показать все команды

🧠 **Текущий режим:** {ai_status} толкования (БЕСПЛАТНО!)
🌟 **Помните:** карты дарят мудрость только раз в день!

💫 Используйте команды выше для взаимодействия с ботом.
            """
            
            await update.message.reply_text(help_message, parse_mode='Markdown')
            
            logger.info(f"💬 Пользователь {user.id} отправил текстовое сообщение: {message_text[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения от {user.id}: {e}")
            
            # Fallback сообщение в случае ошибки
            fallback_message = """
🔮 Привет! Я бот Таро предсказаний.

Используйте /fortune для получения предсказания или /help для справки.

✨ Пусть карты направляют ваш путь!
            """
            
            await update.message.reply_text(fallback_message)
