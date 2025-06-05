# -*- coding: utf-8 -*-
"""
Модель карты Таро
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum

class CardType(Enum):
    """Тип карты Таро"""
    MAJOR_ARCANA = "major_arcana"
    MINOR_ARCANA = "minor_arcana"

class Suit(Enum):
    """Масти Младших Арканов"""
    CUPS = "cups"      # Кубки
    PENTACLES = "pentacles"  # Пентакли  
    SWORDS = "swords"  # Мечи
    WANDS = "wands"    # Жезлы

@dataclass
class TarotCard:
    """Модель карты Таро"""
    
    name: str
    meaning: str
    card_type: Optional[CardType] = None
    suit: Optional[Suit] = None
    
    def __post_init__(self):
        """Определить тип карты автоматически"""
        if self.card_type is None:
            self.card_type = self._determine_card_type()
        
        if self.suit is None and self.card_type == CardType.MINOR_ARCANA:
            self.suit = self._determine_suit()
    
    def _determine_card_type(self) -> CardType:
        """Определить тип карты по названию"""
        minor_arcana_keywords = ["Кубков", "Пентаклей", "Мечей", "Жезлов"]
        
        for keyword in minor_arcana_keywords:
            if keyword in self.name:
                return CardType.MINOR_ARCANA
        
        return CardType.MAJOR_ARCANA
    
    def _determine_suit(self) -> Optional[Suit]:
        """Определить масть карты"""
        if "Кубков" in self.name:
            return Suit.CUPS
        elif "Пентаклей" in self.name:
            return Suit.PENTACLES
        elif "Мечей" in self.name:
            return Suit.SWORDS
        elif "Жезлов" in self.name:
            return Suit.WANDS
        
        return None
    
    @property
    def is_major_arcana(self) -> bool:
        """Проверить, является ли карта Старшим Арканом"""
        return self.card_type == CardType.MAJOR_ARCANA
    
    @property
    def is_minor_arcana(self) -> bool:
        """Проверить, является ли карта Младшим Арканом"""
        return self.card_type == CardType.MINOR_ARCANA
    
    def get_suit_emoji(self) -> str:
        """Получить эмодзи масти"""
        suit_emojis = {
            Suit.CUPS: "💧",      # Вода
            Suit.PENTACLES: "🌍", # Земля
            Suit.SWORDS: "💨",    # Воздух
            Suit.WANDS: "🔥"      # Огонь
        }
        
        return suit_emojis.get(self.suit, "🎴")
    
    def get_type_emoji(self) -> str:
        """Получить эмодзи типа карты"""
        if self.is_major_arcana:
            return "🔮"
        else:
            return self.get_suit_emoji()
    
    def __str__(self) -> str:
        """Строковое представление карты"""
        emoji = self.get_type_emoji()
        return f"{emoji} {self.name}"
