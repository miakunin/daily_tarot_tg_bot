# -*- coding: utf-8 -*-
"""
Сервис для работы с AI (Groq)
"""

import logging
from typing import Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..config import Config

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """Ты мастер Таро. Создай краткое толкование карты "{card_name}"{user_part}.

Требования:
- Тон: мистический, мудрый, доброжелательный
- Длина: ровно 3 предложения, не больше
- 1-2 красивых эмоджи на всё толкование (🌟✨🔮💫🌙)
- Пиши на русском языке
- Избегай негативных предсказаний

Структура:
1. Энергия карты и её значение на сегодня (1 предложение)
2. Как это проявится в делах, отношениях или росте (1 предложение)
3. Практический совет на день (1 предложение)

Ответь только толкованием, без вступлений и комментариев."""


class AIService:
    """Сервис для AI толкований через Groq"""

    def __init__(self, config: Config):
        self.config = config
        self._groq_client: Optional[OpenAI] = None

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
        """Сгенерировать толкование через Groq. Вернуть None если провайдер недоступен."""
        if not self._groq_client:
            logger.error("❌ Groq недоступен")
            return None

        user_part = f" для {user_name}" if user_name else ""
        prompt = PROMPT_TEMPLATE.format(card_name=card_name, user_part=user_part)

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

        logger.error("❌ Все модели Groq недоступны")
        return None

    @property
    def ai_available(self) -> bool:
        return self._groq_client is not None
