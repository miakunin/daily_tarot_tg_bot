# -*- coding: utf-8 -*-
"""
Сервис для работы с базой данных (JSON файл)
"""

import json
import os
import shutil
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Database:
    """Простая JSON база данных для пользователей"""
    
    def __init__(self, filename: str):
        """Инициализация базы данных"""
        self.filename = filename
        # Создать директорию если не существует
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        logger.info(f"💾 Database инициализирована: {filename}")
    
    def load_all_data(self) -> Dict[str, Dict[str, Any]]:
        """Загрузить все данные из файла"""
        try:
            if not os.path.exists(self.filename):
                return {}
            
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except json.JSONDecodeError:
            logger.error(f"❌ Ошибка чтения JSON файла: {self.filename}")
            return {}
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки данных: {e}")
            return {}
    
    def save_all_data(self, data: Dict[str, Dict[str, Any]]):
        """Сохранить все данные в файл"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения данных: {e}")
    
    def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить данные пользователя"""
        all_data = self.load_all_data()
        return all_data.get(str(user_id))
    
    def save_user_data(self, user_id: int, user_data: Dict[str, Any]):
        """Сохранить данные пользователя"""
        all_data = self.load_all_data()
        all_data[str(user_id)] = user_data
        self.save_all_data(all_data)
    
    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        all_data = self.load_all_data()
        user_key = str(user_id)
        
        if user_key in all_data:
            del all_data[user_key]
            self.save_all_data(all_data)
            logger.info(f"🗑️ Пользователь {user_id} удален")
            return True
        
        return False
    
    def reset_with_backup(self) -> str:
        """Сбросить базу данных с созданием бэкапа"""
        backup_path = ""

        if os.path.exists(self.filename):
            backup_dir = os.path.join(os.path.dirname(self.filename), 'backups')
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f"users_data_backup_{timestamp}.json")
            shutil.copy(self.filename, backup_path)

            os.remove(self.filename)
            logger.info(f"💾 Создан бэкап: {backup_path}")

        return backup_path
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику базы данных"""
        if not os.path.exists(self.filename):
            return {
                'exists': False,
                'size': 0,
                'users_count': 0
            }
        
        try:
            # Размер файла
            file_size = os.path.getsize(self.filename)
            
            # Количество пользователей
            data = self.load_all_data()
            users_count = len(data)
            
            return {
                'exists': True,
                'size': file_size,
                'users_count': users_count,
                'filename': self.filename
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {
                'exists': True,
                'size': 0,
                'users_count': 0,
                'error': str(e)
            }
