# -*- coding: utf-8 -*-
"""
Админские обработчики команд (/reset, /adminstats)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..config import Config
from ..services.user_service import UserService
from ..data.tarot_cards import get_total_cards

logger = logging.getLogger(__name__)

class AdminHandlers:
    """Обработчики админских команд"""
    
    def __init__(self, config: Config, user_service: UserService):
        """Инициализация обработчиков"""
        self.config = config
        self.user_service = user_service
    
    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /reset - сброс базы данных"""
        user_id = update.effective_user.id
        
        # Проверить права админа
        if not self.user_service.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        try:
            # Сбросить базу данных
            result = self.user_service.reset_database()
            
            if result['status'] == 'success':
                reset_message = f"""
🔧 **База данных сброшена!**

✅ Старая база сохранена как: `{result['backup_file']}`
🗑️ Активная база очищена
🔄 Все пользователи смогут получить новое предсказание

⚠️ Это действие необратимо!
                """
            else:
                reset_message = f"❌ Ошибка сброса базы данных: {result['message']}"
            
            await update.message.reply_text(reset_message, parse_mode='Markdown')
            logger.warning(f"🔧 Админ {user_id} сбросил базу данных")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Критическая ошибка: {e}")
            logger.error(f"❌ Ошибка сброса БД админом {user_id}: {e}")
    
    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /adminstats - статистика бота"""
        user_id = update.effective_user.id
        
        # Проверить права админа
        if not self.user_service.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        try:
            # Получить статистику
            stats = self.user_service.get_all_stats()
            config_status = self.config.get_status_info()
            
            stats_message = f"""
📊 **Статистика бота:**

👥 **Пользователи:**
• Всего пользователей: {stats['total_users']}
• Активных сегодня: {stats['users_today']}
• Всего предсказаний: {stats['total_fortunes']}

🎴 **Контент:**
• Карт в колоде: {get_total_cards()}

🤖 **AI система:**
• AI доступны: {"✅ Да" if config_status['ai_available'] else "❌ Нет"}
• AI включены: {"✅ Да" if config_status['ai_enabled'] else "❌ Нет"}

💾 **База данных:**
• Файл: `{stats['database_file']}`

⚙️ **Админ команды:**
/reset - сбросить базу данных
/adminstats - эта статистика

👑 Админ ID: {self.config.admin_id}
            """
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            logger.info(f"📊 Админ {user_id} запросил статистику")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения статистики: {e}")
            logger.error(f"❌ Ошибка статистики для админа {user_id}: {e}")
