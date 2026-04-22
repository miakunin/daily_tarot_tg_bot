# -*- coding: utf-8 -*-
"""
Базовые обработчики команд (/start, /help)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..config import Config
from ..services.user_service import UserService
from ..data.tarot_cards import get_cards_by_type

logger = logging.getLogger(__name__)

class BasicHandlers:
    """Обработчики базовых команд"""
    
    def __init__(self, config: Config, user_service: UserService):
        """Инициализация обработчиков"""
        self.config = config
        self.user_service = user_service
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start"""
        user = update.effective_user
        user_name = user.first_name or "друг"
        
        # Регистрация/обновление пользователя
        self.user_service.get_user(user.id, user.first_name)
        
        card_stats = get_cards_by_type()
        ai_status = "🤖 AI толкования" if self.config.get_status_info()['ai_enabled'] else "📚 Классические"
        
        welcome_message = f"""
🔮 Добро пожаловать в бот Ежедневных Предсказаний Таро, {user_name}! 🔮

✨ Я даю только ОДНО предсказание в день - как настоящий мастер Таро.

🎴 **Моя колода содержит {card_stats['total']} карт:**
🔮 {card_stats['major_arcana']} Старших Арканов
⚔️ {card_stats['minor_arcana']} Младших Арканов (все 4 масти)

🧠 **Режим толкований:** {ai_status} 💰 БЕСПЛАТНО!

**Команды:**
/fortune - Получить своё ежедневное предсказание
/card - То же, что и /fortune
/stats - Посмотреть вашу статистику
/deck - Информация о колоде
/ai - Переключить режим толкований
/help - Показать справку

🌟 Готовы узнать, что уготовили вам карты сегодня? 
Используйте /fortune чтобы получить своё уникальное послание!

💫 Помните: карты дают мудрость лишь раз в день.
        """
        
        await update.message.reply_text(welcome_message)
        logger.info(f"👋 Пользователь {user.id} выполнил /start")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        status = self.config.get_status_info()
        ai_status = "🤖 включены" if status['ai_enabled'] else "📚 выключены"
        ai_availability = "" if status['ai_available'] else "\n❌ AI недоступны (нет Groq API ключа)"
        
        help_message = f"""
🃏 **Команды бота Предсказаний Таро:**

**Основные команды:**
/fortune - Получить ежедневное предсказание Таро
/card - То же, что и /fortune
/stats - Посмотреть вашу статистику  
/deck - Информация о колоде карт

**AI и настройки:**
/ai - Переключить режим толкований (AI/классические)
/status - Проверить статус AI системы

**Помощь:**
/start - Приветственное сообщение
/help - Показать эту справку

✨ **Особенности бота:**
🌙 Только одно предсказание в день на человека
🔮 Уникальные послания для каждого пользователя
📊 Статистика ваших обращений к картам
🎴 Полная колода из 78 карт Таро
🤖 AI толкования: {ai_status} (БЕСПЛАТНО!){ai_availability}

*Помните: чтения Таро предназначены для развлечения и самоанализа.*

💫 Пусть карты направляют ваш путь!
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
        logger.info(f"❓ Пользователь {update.effective_user.id} запросил помощь")
