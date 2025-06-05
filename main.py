#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Tarot Fortune Bot
Главная точка входа в приложение
"""

import logging
import asyncio
from bot.config import Config
from bot.bot import TarotBot

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def main():
    """Главная функция запуска бота"""
    # Настроить логирование
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Загрузить конфигурацию
        config = Config()
        
        # Создать и запустить бота
        bot = TarotBot(config)
        
        logger.info("🔮 Запуск Tarot Fortune Bot...")
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == '__main__':
    main()
