# -*- coding: utf-8 -*-
"""
Обработчики команд статистики (/stats, /deck)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..config import Config
from ..services.user_service import UserService
from ..data.tarot_cards import get_cards_by_type, get_total_cards

logger = logging.getLogger(__name__)

class StatsHandlers:
    """Обработчики команд статистики"""
    
    def __init__(self, config: Config, user_service: UserService):
        """Инициализация обработчиков"""
        self.config = config
        self.user_service = user_service
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /stats"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "друг"
        
        try:
            # Получить статистику пользователя
            user = self.user_service.get_user(user_id, update.effective_user.first_name)
            
            if user.total_fortunes == 0:
                stats_message = f"""
📊 {user_name}, ваша статистика пока пуста...

🔮 Вы ещё не получали предсказаний от карт.
✨ Используйте /fortune чтобы получить своё первое послание!

💫 Пусть путешествие в мир Таро начнётся!
                """
            else:
                # Проверить, можно ли получить предсказание сегодня
                can_get_today = user.can_get_fortune_today
                status = "✅ Доступно" if can_get_today else "⏳ Ждите до завтра"
                
                stats_message = f"""
📊 **Статистика {user_name}:**

🔮 Всего предсказаний: {user.total_fortunes}
📅 Последнее предсказание: {user.last_fortune_date or 'неизвестно'}
🎂 Зарегистрирован: {user.created_at or 'неизвестно'}
🌟 Сегодняшнее предсказание: {status}

✨ Каждое обращение к картам приближает вас к мудрости!
                """
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            logger.info(f"📊 Пользователь {user_id} запросил статистику")
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики для {user_id}: {e}")
            await update.message.reply_text("❌ Произошла ошибка при получении статистики. Попробуйте позже.")
    
    async def deck_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /deck - информация о колоде"""
        try:
            card_stats = get_cards_by_type()
            
            deck_message = f"""
🃏 **Информация о колоде Таро:**

📊 **Статистика карт:**
🔮 Старшие Арканы: {card_stats['major_arcana']} карт
⚔️ Младшие Арканы: {card_stats['minor_arcana']} карт
🎴 Всего карт в колоде: {card_stats['total']} карт

🌟 **Младшие Арканы включают все четыре масти:**
💧 Кубки (Вода) - эмоции, отношения, духовность
🌍 Пентакли (Земля) - материальный мир, финансы, карьера  
💨 Мечи (Воздух) - мысли, конфликты, общение
🔥 Жезлы (Огонь) - действие, энергия, творчество

✨ Каждое предсказание уникально и выбирается случайным образом из полной колоды!

🎯 **Система предсказаний:**
🌙 Одно предсказание в день на человека
🤖 AI толкования от Groq (БЕСПЛАТНО!)
📚 Fallback на классические толкования карт
            """
            
            await update.message.reply_text(deck_message, parse_mode='Markdown')
            logger.info(f"🎴 Пользователь {update.effective_user.id} запросил информацию о колоде")
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о колоде: {e}")
            await update.message.reply_text("❌ Произошла ошибка при получении информации о колоде.")
