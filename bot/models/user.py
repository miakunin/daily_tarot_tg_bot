# -*- coding: utf-8 -*-
"""
Модель пользователя
"""

from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional

@dataclass
class User:
    """Модель пользователя бота"""
    
    user_id: int
    last_fortune_date: Optional[str] = None
    total_fortunes: int = 0
    first_name: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        """Инициализация после создания"""
        if self.created_at is None:
            self.created_at = date.today().isoformat()
    
    @property
    def can_get_fortune_today(self) -> bool:
        """Проверить, может ли пользователь получить предсказание сегодня"""
        if self.last_fortune_date is None:
            return True
        
        today = date.today().isoformat()
        return self.last_fortune_date != today
    
    def update_fortune_date(self):
        """Обновить дату последнего предсказания"""
        self.last_fortune_date = date.today().isoformat()
        self.total_fortunes += 1
    
    def to_dict(self) -> dict:
        """Преобразовать в словарь для сохранения"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, user_id: int, data: dict) -> 'User':
        """Создать пользователя из словаря"""
        return cls(
            user_id=user_id,
            last_fortune_date=data.get('last_fortune_date'),
            total_fortunes=data.get('total_fortunes', 0),
            first_name=data.get('first_name'),
            created_at=data.get('created_at')
        )
    
    def get_stats_text(self) -> str:
        """Получить текстовое представление статистики"""
        return f"""
📊 **Ваша статистика:**

🔮 Всего предсказаний: {self.total_fortunes}
📅 Последнее предсказание: {self.last_fortune_date or 'никогда'}
🎂 Зарегистрирован: {self.created_at or 'неизвестно'}
🌟 Сегодняшнее предсказание: {"✅ Доступно" if self.can_get_fortune_today else "⏳ Ждите до завтра"}

✨ Каждое обращение к картам приближает вас к мудрости!
        """
