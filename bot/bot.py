# -*- coding: utf-8 -*-
"""
Основной класс Telegram бота
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .config import Config
from .services.ai_service import AIService
from .services.user_service import UserService
from .services.fortune_service import FortuneService
from .data.tarot_cards import get_total_cards, get_cards_by_type

# Импорт обработчиков
from .handlers.basic import BasicHandlers
from .handlers.fortune import FortuneHandlers
from .handlers.stats import StatsHandlers
from .handlers.ai import AIHandlers
from .handlers.admin import AdminHandlers
from .handlers.messages import MessageHandlers

logger = logging.getLogger(__name__)

class TarotBot:
    """Основной класс Tarot Fortune Bot"""
    
    def __init__(self, config: Config):
        """Инициализация бота"""
        self.config = config
        
        # Инициализация сервисов
        self.ai_service = AIService(config)
        self.user_service = UserService(config)
        self.fortune_service = FortuneService(config, self.ai_service, self.user_service)
        
        # Создание приложения
        self.application = Application.builder().token(config.bot_token).build()
        
        # Инициализация обработчиков
        self._setup_handlers()
        
        logger.info("🤖 TarotBot инициализирован")
    
    def _setup_handlers(self):
        """Настройка обработчиков команд"""
        # Создание экземпляров обработчиков
        basic_handlers = BasicHandlers(self.config, self.user_service)
        fortune_handlers = FortuneHandlers(self.config, self.fortune_service)
        stats_handlers = StatsHandlers(self.config, self.user_service)
        ai_handlers = AIHandlers(self.config, self.ai_service, self.user_service)
        admin_handlers = AdminHandlers(self.config, self.user_service)
        message_handlers = MessageHandlers(self.config)
        
        # Регистрация основных команд
        self.application.add_handler(CommandHandler("start", basic_handlers.start))
        self.application.add_handler(CommandHandler("help", basic_handlers.help))
        
        # Команды предсказаний
        self.application.add_handler(CommandHandler("fortune", fortune_handlers.fortune))
        self.application.add_handler(CommandHandler("card", fortune_handlers.fortune))
        
        # Статистика и информация
        self.application.add_handler(CommandHandler("stats", stats_handlers.stats))
        self.application.add_handler(CommandHandler("deck", stats_handlers.deck_info))
        
        # AI команды
        self.application.add_handler(CommandHandler("ai", ai_handlers.toggle))
        self.application.add_handler(CommandHandler("status", ai_handlers.status))
        
        # Админские команды
        self.application.add_handler(CommandHandler("reset", admin_handlers.reset))
        self.application.add_handler(CommandHandler("adminstats", admin_handlers.admin_stats))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.handle_text)
        )
        
        logger.info("📋 Обработчики команд настроены")
    
    def run(self):
        """Запуск бота"""
        # Информация о запуске
        self._print_startup_info()
        
        try:
            # Запуск polling
            self.application.run_polling(allowed_updates=['message', 'callback_query'])
        except KeyboardInterrupt:
            logger.info("👋 Получен сигнал завершения")
        except Exception as e:
            logger.error(f"❌ Ошибка при работе бота: {e}")
            raise
        finally:
            logger.info("🔮 Бот завершил работу")
    
    def _print_startup_info(self):
        """Вывод информации при запуске"""
        card_stats = get_cards_by_type()
        status = self.config.get_status_info()
        
        ai_status = "✅ доступны (БЕСПЛАТНО)" if status['ai_enabled'] else "❌ недоступны"
        admin_status = f"✅ настроен ({self.config.admin_id})" if status['admin_configured'] else "❌ не настроен"
        
        print("🔮 Бот Ежедневных Предсказаний Таро запущен...")
        print("✨ Система ограничений активна: одно предсказание в день!")
        print(f"🎴 Колода содержит: {card_stats['total']} карт ({card_stats['major_arcana']} старших + {card_stats['minor_arcana']} младших)")
        print(f"🤖 AI толкования (Groq): {ai_status}")
        print(f"👑 Админ доступ: {admin_status}")
        print("Используйте Ctrl+C чтобы остановить бота")
