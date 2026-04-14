# -*- coding: utf-8 -*-
"""
Сервис для работы с AI (Google Gemini)
"""

import logging
from typing import Optional, List

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from ..config import Config

logger = logging.getLogger(__name__)

class AIService:
    """Сервис для работы с AI толкованиями"""
    
    def __init__(self, config: Config):
        """Инициализация AI сервиса"""
        self.config = config
        self._initialized = False

        if GEMINI_AVAILABLE and config.gemini_api_key:
            try:
                genai.configure(api_key=config.gemini_api_key)
                self._initialized = True
                logger.info("🤖 Google Gemini API инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Gemini: {e}")
        else:
            if not GEMINI_AVAILABLE:
                logger.warning("⚠️ Google Generative AI не установлен")
            else:
                logger.warning("⚠️ GEMINI_API_KEY не найден")
    
    async def generate_interpretation(self, card_name: str, user_name: Optional[str] = None) -> Optional[str]:
        """Генерировать AI толкование карты"""
        if not self.ai_available:
            return None
        
        try:
            # Создать персонализированный промпт
            user_part = f" для {user_name}" if user_name else ""
            
            prompt = f"""Ты мастер Таро с многолетним опытом. Создай персонализированное толкование карты "{card_name}"{user_part}.

Требования:
- Тон: мистический, мудрый, но доброжелательный
- Длина: 6-8 предложений (полноценное толкование)
- Используй красивые эмоджи (🌟✨🔮💫🌙)
- Пиши на русском языке
- Избегай негативных предсказаний, даже для "сложных" карт

Структура толкования:
1. Общее значение карты и её энергия (2 предложения)
2. Что это означает для сегодняшнего дня: любовь, работа или личностный рост (2-3 предложения)
3. Практический совет и напутствие на день (2 предложения)

Карта: {card_name}

Ответь только толкованием, без дополнительных комментариев."""

            # Попробовать разные модели
            for model_name in self.config.gemini_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    
                    generation_config = genai.types.GenerationConfig(
                        temperature=0.8,
                        max_output_tokens=500,
                        top_p=0.9,
                        top_k=40
                    )
                    
                    response = model.generate_content(prompt, generation_config=generation_config)
                    
                    if response.text:
                        interpretation = response.text.strip()
                        logger.info(f"✅ AI толкование сгенерировано для {card_name} (модель: {model_name})")
                        return interpretation
                    
                except Exception as model_error:
                    logger.warning(f"⚠️ Модель {model_name} недоступна: {model_error}")
                    continue
            
            logger.error("❌ Все модели Gemini недоступны")
            return None
            
        except Exception as e:
            self._handle_ai_error(e)
            return None
    
    def _handle_ai_error(self, error: Exception):
        """Обработка ошибок AI"""
        error_msg = str(error).lower()
        
        if "quota" in error_msg or "limit" in error_msg:
            logger.warning("⚠️ Gemini API: Превышена квота")
        elif "api_key" in error_msg or "authentication" in error_msg:
            logger.error("❌ Gemini API: Проблема с API ключом")
        elif "safety" in error_msg or "blocked" in error_msg:
            logger.warning("⚠️ Gemini API: Контент заблокирован фильтрами")
        elif "404" in error_msg or "not found" in error_msg:
            logger.error("❌ Gemini API: Модель не найдена. Обновите библиотеку")
        else:
            logger.error(f"❌ Ошибка Gemini API: {error}")
    
    async def get_available_models(self) -> List[str]:
        """Получить список доступных моделей"""
        if not GEMINI_AVAILABLE or not self.config.gemini_api_key:
            return []
        
        try:
            models = genai.list_models()
            available_models = []
            
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            
            return available_models
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения моделей: {e}")
            return []
    
    @property
    def ai_available(self) -> bool:
        """Проверить доступность AI (ключ настроен и библиотека установлена)"""
        return self._initialized
