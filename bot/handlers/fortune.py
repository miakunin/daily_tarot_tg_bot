# -*- coding: utf-8 -*-
"""
Обработчики команд предсказаний (/fortune, /card)
"""

import logging
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from ..config import Config
from ..services.fortune_service import FortuneService

logger = logging.getLogger(__name__)

ERROR_MESSAGE = (
    "❌ Произошла ошибка при генерации предсказания.\n\n"
    "🔄 Пожалуйста, попробуйте снова через несколько секунд.\n"
    "📞 Если проблема повторится, используйте /help для получения поддержки."
)


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
        placeholder = None

        try:
            # Отправить placeholder пока генерируется предсказание
            placeholder = await update.message.reply_text("🔮 Тасую карты и раскладываю расклад...")

            # Получить предсказание
            result = await self.fortune_service.get_daily_fortune(user.id, user.first_name)

            # Форматировать и заменить placeholder ответом
            response_message = self.fortune_service.format_fortune_response(user_name, result)

            # Попробовать с Markdown; если AI вернул сломанный Markdown — отправить plain text
            try:
                await placeholder.edit_text(response_message, parse_mode='Markdown')
            except BadRequest:
                logger.warning(f"⚠️ Markdown parse failed for user {user.id}, falling back to plain text")
                await placeholder.edit_text(response_message)

            # Логирование
            if result['success']:
                card_name = result['card'].name
                ai_used = "AI" if result['ai_used'] else "классическое"
                logger.info(f"🔮 Пользователь {user.id} получил предсказание: {card_name} ({ai_used})")
            else:
                logger.info(f"⏳ Пользователь {user.id} уже получал предсказание сегодня")

        except Exception as e:
            logger.error(f"❌ Ошибка обработки предсказания для {user.id}: {e}")

            # Редактировать placeholder если он был отправлен, иначе отправить новое сообщение
            if placeholder:
                try:
                    await placeholder.edit_text(ERROR_MESSAGE)
                    return
                except Exception:
                    pass
            await update.message.reply_text(ERROR_MESSAGE)
