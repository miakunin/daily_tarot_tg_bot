# -*- coding: utf-8 -*-
"""
Обработчики AI команд (/ai, /status)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..config import Config
from ..services.ai_service import AIService

logger = logging.getLogger(__name__)

class AIHandlers:
    """Обработчики AI команд"""
    
    def __init__(self, config: Config, ai_service: AIService):
        """Инициализация обработчиков"""
        self.config = config
        self.ai_service = ai_service
    
    async def toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /ai - переключение режима толкований"""
        user_id = update.effective_user.id
        
        try:
            if not self.ai_service.ai_available:
                await update.message.reply_text(
                    "❌ AI толкования недоступны.\n\n"
                    "Для включения добавьте GEMINI_API_KEY в .env файл и установите: pip install google-generativeai"
                )
                return
            
            # Переключить режим
            new_state = self.ai_service.toggle_ai()
            
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
            logger.info(f"🔄 Пользователь {user_id} переключил AI: {status}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка переключения AI для {user_id}: {e}")
            await update.message.reply_text("❌ Произошла ошибка при переключении режима толкований.")
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /status - статус AI системы"""
        user_id = update.effective_user.id
        
        try:
            if not self.ai_service.ai_available:
                if not hasattr(self.ai_service, '__class__'): # Проверка на наличие Gemini библиотеки
                    status_message = """
❌ **Статус AI: Недоступен**

📦 Google Generative AI библиотека не установлена
💡 Для установки: `pip install --upgrade google-generativeai`
🔄 Используются классические толкования карт
                    """
                else:
                    status_message = """
⚠️ **Статус AI: Не настроен**

🔑 GEMINI_API_KEY не найден в .env файле
🌐 Получите ключ БЕСПЛАТНО на: https://makersuite.google.com/app/apikey
🔄 Используются классические толкования карт
                    """
            else:
                # Попробуем сделать тестовый запрос
                test_result = await self.ai_service.generate_interpretation("Дурак", "тест")
                
                if test_result:
                    # Получить список доступных моделей
                    available_models = await self.ai_service.get_available_models()
                    models_text = "\n".join([f"  • {model}" for model in available_models[:5]])  # Показать первые 5
                    if len(available_models) > 5:
                        models_text += f"\n  • ... и ещё {len(available_models) - 5} моделей"
                    
                    status_message = f"""
✅ **Статус AI: Работает**

🤖 Google Gemini API подключён и функционирует
🔮 AI толкования: {"включены" if self.ai_service.ai_enabled else "выключены"}
🎯 Активная модель: Gemini-1.5-Flash (приоритет)
✨ Персонализированные толкования доступны
💰 Бесплатный лимит: 60 запросов в минуту

📋 **Доступные модели:**
{models_text if models_text else "  • Загрузка..."}

💡 Используйте /ai чтобы переключить режим
                    """
                else:
                    status_message = """
❌ **Статус AI: Ошибка**

🔑 API ключ настроен, но есть проблемы:
• Модели недоступны или устарели
• Обновите библиотеку: pip install --upgrade google-generativeai
• Возможно, превышен лимит запросов (60/мин)
• Проблемы с сетью

🔄 Автоматически используются классические толкования
📊 Проверьте ключ на: https://makersuite.google.com/
                    """
            
            await update.message.reply_text(status_message, parse_mode='Markdown')
            logger.info(f"🔍 Пользователь {user_id} проверил статус AI")
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки статуса AI для {user_id}: {e}")
            await update.message.reply_text("❌ Произошла ошибка при проверке статуса AI системы.")
