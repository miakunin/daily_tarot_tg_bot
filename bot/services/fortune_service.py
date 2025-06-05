# -*- coding: utf-8 -*-
"""
Сервис для работы с предсказаниями
"""

import logging
import random
from typing import Optional

from ..config import Config
from ..models.card import TarotCard
from ..data.tarot_cards import tarot_deck, fortune_templates
from .ai_service import AIService
from .user_service import UserService

logger = logging.getLogger(__name__)

class FortuneService:
    """Сервис для генерации предсказаний"""
    
    def __init__(self, config: Config, ai_service: AIService, user_service: UserService):
        """Инициализация сервиса предсказаний"""
        self.config = config
        self.ai_service = ai_service
        self.user_service = user_service
        
        # Преобразовать данные карт в объекты TarotCard
        self.cards = [TarotCard(name=card['name'], meaning=card['meaning']) for card in tarot_deck]
        
        logger.info(f"🎴 FortuneService инициализирован с {len(self.cards)} картами")
    
    def draw_random_card(self) -> TarotCard:
        """Вытянуть случайную карту из колоды"""
        return random.choice(self.cards)
    
    async def generate_fortune_message(self, card: TarotCard, user_name: Optional[str] = None) -> str:
        """Сгенерировать сообщение с предсказанием"""
        # Попробовать получить AI толкование
        if self.ai_service.ai_enabled:
            ai_interpretation = await self.ai_service.generate_interpretation(card.name, user_name)
            
            if ai_interpretation:
                return self._format_ai_fortune(card, ai_interpretation)
        
        # Fallback на классическое толкование
        return self._format_classic_fortune(card)
    
    def _format_ai_fortune(self, card: TarotCard, ai_interpretation: str) -> str:
        """Форматировать AI предсказание"""
        ai_templates = [
            "🔮 Карта дня - **{name}**\n\n{ai_meaning}\n\n💫 Пусть это послание направляет вас сегодня!",
            "🌟 Вселенная открывает **{name}** для вас сегодня.\n\n{ai_meaning}\n\n🙏 Доверьтесь мудрости карт.",
            "✨ Карты заговорили! **{name}** несёт особое послание.\n\n{ai_meaning}\n\n🌙 Примите это руководство с открытым сердцем."
        ]
        
        template = random.choice(ai_templates)
        return template.format(name=card.name, ai_meaning=ai_interpretation)
    
    def _format_classic_fortune(self, card: TarotCard) -> str:
        """Форматировать классическое предсказание"""
        template = random.choice(fortune_templates)
        return template.format(name=card.name, meaning=card.meaning)
    
    async def get_daily_fortune(self, user_id: int, first_name: Optional[str] = None) -> dict:
        """Получить ежедневное предсказание для пользователя"""
        # Проверить возможность получения предсказания
        if not self.user_service.can_get_fortune(user_id):
            user_stats = self.user_service.get_user_stats(user_id)
            return {
                'success': False,
                'type': 'already_used',
                'stats': user_stats
            }
        
        # Вытянуть карту
        card = self.draw_random_card()
        
        # Обновить данные пользователя
        self.user_service.update_fortune_date(user_id, first_name)
        
        # Сгенерировать предсказание
        fortune_message = await self.generate_fortune_message(card, first_name)
        
        # Получить обновлённую статистику
        updated_stats = self.user_service.get_user_stats(user_id)
        
        return {
            'success': True,
            'type': 'new_fortune',
            'card': card,
            'message': fortune_message,
            'stats': updated_stats,
            'ai_used': self.ai_service.ai_enabled
        }
    
    def get_waiting_message(self, user_name: str, stats: dict) -> str:
        """Получить сообщение ожидания"""
        return f"""
🌙 {user_name}, карты уже открыли вам свои тайны сегодня...

✨ Вселенная дарует только одно предсказание в день. 
🕐 Возвращайтесь завтра, чтобы узнать, что готовят вам звёзды.

📊 Ваша статистика:
🔮 Всего предсказаний: {stats.get('total_fortunes', 0)}
📅 Последнее предсказание: {stats.get('last_fortune_date', 'неизвестно')}

💫 Пусть сегодняшнее послание направляет вас до завтрашнего рассвета!
        """
    
    def format_fortune_response(self, user_name: str, result: dict) -> str:
        """Форматировать итоговый ответ с предсказанием"""
        if not result['success']:
            return self.get_waiting_message(user_name, result['stats'])
        
        stats = result['stats']
        message = result['message']
        
        # Информация об источнике толкования
        source_info = "🤖 Персональное Gemini толкование" if result['ai_used'] else "📚 Классическое толкование"
        
        # Основное сообщение
        full_message = f"Привет, {user_name}! 🌟\n\n{message}\n\n"
        
        # Добавить информацию о количестве предсказаний
        total = stats.get('total_fortunes', 0)
        if total == 1:
            full_message += "🎉 Это ваше первое предсказание! Добро пожаловать в мир Таро!\n\n"
        else:
            full_message += f"📊 Это ваше {total}-е предсказание\n\n"
        
        full_message += f"{source_info}\n💫 Помните: новое предсказание будет доступно завтра!"
        
        return full_message
