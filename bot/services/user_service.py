# -*- coding: utf-8 -*-
"""
Сервис для работы с пользователями
"""

import logging
from typing import Optional, Dict, Any
from datetime import date

from ..config import Config
from ..models.user import User
from .database import Database

logger = logging.getLogger(__name__)

class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, config: Config):
        """Инициализация сервиса пользователей"""
        self.config = config
        self.db = Database(config.user_data_file)
        logger.info("👥 UserService инициализирован")
    
    def get_user(self, user_id: int, first_name: Optional[str] = None) -> User:
        """Получить пользователя или создать нового"""
        user_data = self.db.get_user_data(user_id)
        
        if user_data:
            user = User.from_dict(user_id, user_data)
            # Обновить имя если изменилось
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                self._save_user(user)
        else:
            # Создать нового пользователя
            user = User(
                user_id=user_id,
                first_name=first_name,
                created_at=date.today().isoformat()
            )
            self._save_user(user)
            logger.info(f"👤 Новый пользователь создан: {user_id}")
        
        return user
    
    def _save_user(self, user: User):
        """Сохранить пользователя"""
        self.db.save_user_data(user.user_id, user.to_dict())
    
    def record_fortune(self, user_id: int, first_name: Optional[str] = None) -> Dict[str, Any]:
        """Обновить дату предсказания и вернуть статистику за одну операцию"""
        user = self.get_user(user_id, first_name)
        user.update_fortune_date()
        self._save_user(user)
        logger.info(f"🔮 Пользователь {user_id} получил предсказание")
        return self.user_stats(user)

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        user = self.get_user(user_id)
        return self.user_stats(user)

    @staticmethod
    def user_stats(user: User) -> Dict[str, Any]:
        """Сформировать словарь статистики из объекта User"""
        return {
            'total_fortunes': user.total_fortunes,
            'last_fortune_date': user.last_fortune_date,
            'created_at': user.created_at,
            'can_get_today': user.can_get_fortune_today
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Получить общую статистику всех пользователей"""
        all_data = self.db.load_all_data()
        
        total_users = len(all_data)
        total_fortunes = sum(data.get('total_fortunes', 0) for data in all_data.values())
        
        # Пользователи сегодня
        today = date.today().isoformat()
        users_today = sum(
            1 for data in all_data.values() 
            if data.get('last_fortune_date') == today
        )
        
        return {
            'total_users': total_users,
            'total_fortunes': total_fortunes,
            'users_today': users_today,
            'database_file': self.config.user_data_file
        }
    
    def reset_database(self) -> Dict[str, str]:
        """Сбросить базу данных (создать бэкап)"""
        try:
            backup_file = self.db.reset_with_backup()
            logger.warning(f"🗑️ База данных сброшена, бэкап: {backup_file}")
            return {
                'status': 'success',
                'backup_file': backup_file,
                'message': 'База данных успешно сброшена'
            }
        except Exception as e:
            logger.error(f"❌ Ошибка сброса БД: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка сброса: {e}'
            }
    
    def toggle_ai(self, user_id: int, first_name: Optional[str] = None) -> bool:
        """Переключить AI режим для пользователя. Возвращает новое значение."""
        user = self.get_user(user_id, first_name)
        user.use_ai = not user.use_ai
        self._save_user(user)
        return user.use_ai

    def is_admin(self, user_id: int) -> bool:
        """Проверить права администратора"""
        return self.config.admin_configured and user_id == self.config.admin_id
