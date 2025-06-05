# -*- coding: utf-8 -*-
"""
Обработчики команд предсказаний (/fortune, /card)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..config import Config
from ..services.fortune_service import FortuneService

logger = logging.getLogger(__name__)

class FortuneHandlers:
    """Обработчики команд предсказаний"""
    
    def __init__(self, config: Config, fortune_service: FortuneService):
        """Инициализация обработчиков"""
        self.config = config
        self.fortune_service = fortune_service
    
    async def fortune(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команд /fortune и /card"""
        user = update.effective_user
        user_name = user.first_name or "друг"
        
        try:
            # Показать индикатор "печатает..." для AI запросов
            await update.message.reply_chat_action('typing')
            
            # Получить предсказание
            result = await self.fortune_service.get_daily_fortune(user.id, user.first_name)
            
            # Форматировать и отправить ответ
            response_message = self.fortune_service.format_fortune_response(user_name, result)
            
            await update.message.reply_text(response_message, parse_mode='Markdown')
            
            # Логирование
            if result['success']:
                card_name = result['card'].name
                ai_used = "AI" if result['ai_used'] else "классическое"
                logger.info(f"🔮 Пользователь {user.id} получил предсказание: {card_name} ({ai_used})")
            else:
                logger.info(f"⏳ Пользователь {user.id} уже получал предсказание сегодня")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки предсказания для {user.id}: {e}")
            
            error_message = """
❌ Произошла ошибка при генерации предсказания.

🔄 Пожалуйста, попробуйте снова через несколько секунд.
📞 Если проблема повторится, используйте /help для получения поддержки.
            """
            
            await update.message.reply_text(error_message)
