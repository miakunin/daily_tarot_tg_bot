# -*- coding: utf-8 -*-
"""
Обработчики AI команд (/ai, /status)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..config import Config
from ..services.ai_service import AIService
from ..services.user_service import UserService

logger = logging.getLogger(__name__)

class AIHandlers:
    """Обработчики AI команд"""

    def __init__(self, config: Config, ai_service: AIService, user_service: UserService):
        """Инициализация обработчиков"""
        self.config = config
        self.ai_service = ai_service
        self.user_service = user_service

    async def toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /ai - переключение режима толкований (per-user)"""
        user = update.effective_user

        try:
            if not self.ai_service.ai_available:
                await update.message.reply_text(
                    "❌ AI толкования недоступны.\n\n"
                    "Для включения добавьте GEMINI_API_KEY в .env файл и установите: pip install google-generativeai"
                )
                return

            # Переключить режим для этого пользователя
            new_state = self.user_service.toggle_ai(user.id, user.first_name)

            status = "включены 🤖" if new_state else "выключены 📚"
            mode = "персонализированные Gemini толкования" if new_state else "классические описания карт"

            toggle_message = f"""
🔄 **Режим толкований изменён!**

✨ AI толкования: {status}
🎯 Текущий режим: {mode}

🤖 **Gemini толкования:** Уникальные, персонализированные интерпретации (БЕСПЛАТНО!)
📚 **Классические:** Традиционные значения карт Таро

💡 Используйте /ai чтобы снова переключить режим.
            """

            await update.message.reply_text(toggle_message, parse_mode='Markdown')
            logger.info(f"🔄 Пользователь {user.id} переключил AI: {status}")

        except Exception as e:
            logger.error(f"❌ Ошибка переключения AI для {user.id}: {e}")
            await update.message.reply_text("❌ Произошла ошибка при переключении режима толкований.")
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /status - статус AI системы"""
        user_id = update.effective_user.id

        try:
            if not self.ai_service.ai_available:
                status_message = """
⚠️ **Статус AI: Не настроен**

🔑 GEMINI_API_KEY не найден в .env файле или библиотека не установлена
🌐 Получите ключ БЕСПЛАТНО на: https://makersuite.google.com/app/apikey
💡 Установка: `pip install --upgrade google-generativeai`
🔄 Используются классические толкования карт
                """
            else:
                # Легковесная проверка: список моделей вместо полного запроса на генерацию
                available_models = await self.ai_service.get_available_models()
                priority_model = self.config.gemini_models[0] if self.config.gemini_models else "не задана"

                if available_models:
                    models_text = "\n".join([f"  • {model}" for model in available_models[:5]])
                    if len(available_models) > 5:
                        models_text += f"\n  • ... и ещё {len(available_models) - 5} моделей"

                    status_message = f"""
✅ **Статус AI: Работает**

🤖 Google Gemini API подключён и функционирует
🔮 AI толкования: доступны
🎯 Приоритетная модель: {priority_model}
✨ Персонализированные толкования доступны
💰 Бесплатный лимит: 60 запросов в минуту

📋 **Доступные модели:**
{models_text}

💡 Используйте /ai чтобы переключить режим
                    """
                else:
                    status_message = f"""
❌ **Статус AI: Ошибка**

🔑 API ключ настроен, но модели недоступны:
• Обновите библиотеку: pip install --upgrade google-generativeai
• Возможно, превышен лимит запросов (60/мин)
• Проблемы с сетью

🎯 Приоритетная модель: {priority_model}
🔄 Автоматически используются классические толкования
                    """

            await update.message.reply_text(status_message, parse_mode='Markdown')
            logger.info(f"🔍 Пользователь {user_id} проверил статус AI")

        except Exception as e:
            logger.error(f"❌ Ошибка проверки статуса AI для {user_id}: {e}")
            await update.message.reply_text("❌ Произошла ошибка при проверке статуса AI системы.")
