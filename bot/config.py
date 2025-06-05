# -*- coding: utf-8 -*-
"""
Конфигурация бота
"""

import os
from dotenv import load_dotenv
from typing import Optional, List

# Загрузить переменные окружения
load_dotenv()

class Config:
    """Класс конфигурации бота"""
    
    def __init__(self):
        """Инициализация конфигурации"""
        # Загрузить обязательные переменные
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN не найден! Убедитесь, что он указан в .env файле")
        
        # Загрузить опциональные переменные
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        admin_id_str = os.getenv('ADMIN_ID')
        self.admin_id = None
        if admin_id_str:
            try:
                self.admin_id = int(admin_id_str)
            except ValueError:
                self.admin_id = None
        
        # Настройки AI
        self.use_ai_interpretations = bool(self.gemini_api_key)
        
        # База данных - используем существующую bot/data/
        self.data_dir = os.path.join('bot', 'data', 'users')
        self.user_data_file = os.path.join(self.data_dir, 'users_data.json')
        
        # Приоритет моделей Gemini
        self.gemini_models = [
            'gemini-1.5-flash',
            'gemini-1.5-pro', 
            'gemini-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]
    
    @property
    def ai_available(self) -> bool:
        """Проверить доступность AI"""
        return bool(self.gemini_api_key)
    
    @property
    def admin_configured(self) -> bool:
        """Проверить настройку админа"""
        return self.admin_id is not None
    
    def get_status_info(self) -> dict:
        """Получить информацию о состоянии конфигурации"""
        return {
            'bot_configured': bool(self.bot_token),
            'ai_available': self.ai_available,
            'admin_configured': self.admin_configured,
            'ai_enabled': self.use_ai_interpretations and self.ai_available
        }
