# -*- coding: utf-8 -*-
"""
Сервис для работы с AI (Google Gemini + Groq fallback)
"""

import logging
from typing import Optional, List

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..config import Config

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """Ты мастер Таро с многолетним опытом. Создай персонализированное толкование карты "{card_name}"{user_part}.

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


class AIService:
    """Сервис для AI толкований с несколькими провайдерами"""

    def __init__(self, config: Config):
        self.config = config
        self._gemini_ready = False
        self._groq_client: Optional[OpenAI] = None

        if GEMINI_AVAILABLE and config.gemini_api_key:
            try:
                genai.configure(api_key=config.gemini_api_key)
                self._gemini_ready = True
                logger.info("🤖 Google Gemini API инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Gemini: {e}")
        else:
            logger.warning("⚠️ Gemini недоступен (нет библиотеки или ключа)")

        if OPENAI_AVAILABLE and config.groq_api_key:
            try:
                self._groq_client = OpenAI(
                    api_key=config.groq_api_key,
                    base_url="https://api.groq.com/openai/v1",
                )
                logger.info("🤖 Groq API инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Groq: {e}")
        else:
            logger.warning("⚠️ Groq недоступен (нет библиотеки или ключа)")

    async def generate_interpretation(self, card_name: str, user_name: Optional[str] = None) -> Optional[str]:
        """Попробовать Gemini, затем Groq. Вернуть None если оба провайдера недоступны."""
        user_part = f" для {user_name}" if user_name else ""
        prompt = PROMPT_TEMPLATE.format(card_name=card_name, user_part=user_part)

        if self._gemini_ready:
            text = self._try_gemini(prompt, card_name)
            if text:
                return text

        if self._groq_client:
            text = self._try_groq(prompt, card_name)
            if text:
                return text

        logger.error("❌ Все AI провайдеры недоступны")
        return None

    def _try_gemini(self, prompt: str, card_name: str) -> Optional[str]:
        for model_name in self.config.gemini_models:
            try:
                model = genai.GenerativeModel(model_name)
                generation_config = genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=1500,
                    top_p=0.9,
                    top_k=40,
                )
                response = model.generate_content(prompt, generation_config=generation_config)
                if response.text:
                    logger.info(f"✅ Gemini толкование для {card_name} (модель: {model_name})")
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"⚠️ Gemini модель {model_name} недоступна: {e}")
                continue
        return None

    def _try_groq(self, prompt: str, card_name: str) -> Optional[str]:
        for model_name in self.config.groq_models:
            try:
                response = self._groq_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=1500,
                    top_p=0.9,
                )
                text = response.choices[0].message.content
                if text:
                    logger.info(f"✅ Groq толкование для {card_name} (модель: {model_name})")
                    return text.strip()
            except Exception as e:
                logger.warning(f"⚠️ Groq модель {model_name} недоступна: {e}")
                continue
        return None

    async def get_available_models(self) -> List[str]:
        if not self._gemini_ready:
            return []
        try:
            return [
                m.name for m in genai.list_models()
                if 'generateContent' in m.supported_generation_methods
            ]
        except Exception as e:
            logger.error(f"❌ Ошибка получения моделей: {e}")
            return []

    @property
    def ai_available(self) -> bool:
        return self._gemini_ready or self._groq_client is not None
