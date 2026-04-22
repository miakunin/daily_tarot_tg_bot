# 🔮 Tarot Fortune Bot

Telegram бот для ежедневных предсказаний Таро с AI толкованиями через Groq.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-Latest-blue.svg)](https://core.telegram.org/bots/api)
[![Groq](https://img.shields.io/badge/Groq-AI%20Powered-green.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Возможности

🃏 **Полная колода Таро** - 78 карт (22 Старших + 56 Младших Арканов)  
🤖 **AI толкования** - персонализированные интерпретации через Groq (Llama 3.3)  
🌙 **Ограничение "раз в день"** - как у настоящего мастера Таро  
📊 **Статистика пользователей** - история обращений к картам  
👑 **Админская панель** - управление ботом и базой данных  
💰 **Полностью бесплатно** - никаких платных подписок  

## 🎯 Демонстрация

```
🔮 Пример предсказания:

Карта дня - Маг ✨

🌟 Сегодня вселенная дарует вам силу воплощения желаний в реальность. 
Ваша уверенность и решительность станут ключом к успеху. 
✨ Сосредоточьтесь на главной цели и действуйте смело!

📊 Это ваше 15-е предсказание
🤖 Персональное AI толкование
💫 Помните: новое предсказание будет доступно завтра!
```

## 🚀 Быстрый старт

### 1. Клонировать репозиторий
```bash
git clone https://github.com/miakunin/tarot-fortune-bot.git
cd tarot-fortune-bot
```

### 2. Создать виртуальное окружение
```bash
python -m venv tarot_bot_env
source tarot_bot_env/bin/activate  # Linux/macOS
# tarot_bot_env\Scripts\activate     # Windows
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Настроить конфигурацию
```bash
cp .env.example .env
# Отредактировать .env файл
```

### 5. Запустить бота
```bash
python main.py
```

## ⚙️ Конфигурация

Создайте файл `.env` в корне проекта:

```env
# Обязательно
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Опционально (для AI толкований)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxx

# Опционально (для админ функций)
ADMIN_ID=123456789
```

### Получение токенов:

1. **BOT_TOKEN**: [@BotFather](https://t.me/botfather) → `/newbot`
2. **GROQ_API_KEY**: [Groq Console](https://console.groq.com/keys) (бесплатно!)
3. **ADMIN_ID**: [@userinfobot](https://t.me/userinfobot) (ваш Telegram ID)

## 🎮 Использование

### Основные команды:
- `/start` - Приветствие и инструкции
- `/fortune` - Получить ежедневное предсказание ⭐
- `/stats` - Посмотреть свою статистику
- `/deck` - Информация о колоде карт
- `/help` - Список всех команд

### AI команды:
- `/ai` - Переключить режим толкований (AI/классические)
- `/status` - Проверить статус AI системы

### Админские команды:
- `/reset` - Сбросить базу данных (с бэкапом)
- `/adminstats` - Статистика всего бота

## 🏗️ Архитектура

```
tarot_bot/
├── main.py                     # Точка входа
├── requirements.txt            # Зависимости
├── .env                       # Конфигурация (не в Git)
├── .env.example              # Пример конфигурации
├── .gitignore                # Исключения Git
├── README.md                 # Документация
├── LICENSE                   # Лицензия
│
└── bot/                      # Основной пакет
    ├── config.py             # Конфигурация
    ├── bot.py                # Главный класс
    ├── handlers/             # Обработчики команд
    │   ├── basic.py         # /start, /help
    │   ├── fortune.py       # /fortune, /card
    │   ├── stats.py         # /stats, /deck
    │   ├── ai.py            # /ai, /status
    │   ├── admin.py         # админские команды
    │   └── messages.py      # текстовые сообщения
    ├── services/            # Бизнес-логика
    │   ├── ai_service.py    # Groq AI
    │   ├── user_service.py  # Управление пользователями
    │   ├── fortune_service.py # Логика предсказаний
    │   └── database.py      # Работа с JSON базой
    ├── models/              # Модели данных
    │   ├── user.py         # Модель пользователя
    │   └── card.py         # Модель карты Таро
    └── data/               # Данные проекта
        ├── tarot_cards.py  # Колода карт (статические данные)
        ├── users_data.json # База пользователей (не в Git)
        └── users_data_backup_*.json # Автоматические бэкапы (не в Git)
```

### Принципы дизайна:
- **Разделение ответственности** - каждый модуль отвечает за свою область
- **Dependency Injection** - сервисы внедряются в обработчики
- **Async/await** - асинхронная обработка для производительности
- **Type hints** - статическая типизация для надёжности
- **Единое место данных** - все файлы данных в `bot/data/`

## 🤖 AI Толкования

Бот поддерживает два режима толкований:

### 🧠 Groq AI (рекомендуется)
- **Персонализированные толкования** для каждого пользователя
- **Учёт имени пользователя** в интерпретации
- **Уникальные советы** каждый раз
- **Бесплатный тариф** с щедрыми лимитами
- **Модели:** Llama 3.3 70B (основная), Llama 3.1 8B Instant (fallback)

### 📚 Классические толкования
- **Традиционные значения** карт Таро
- **Быстрая работа** без внешних API
- **Автоматический fallback** если AI недоступен

## 🗄️ База данных

Используется простая JSON база данных с автоматическими бэкапами в `bot/data/`:

```json
{
  "123456789": {
    "last_fortune_date": "2025-06-05",
    "total_fortunes": 15,
    "first_name": "Иван",
    "created_at": "2025-06-01"
  }
}
```

### Особенности:
- **Файловое хранение** - нет необходимости в БД сервере
- **Автоматические бэкапы** при сбросе данных в `bot/data/`
- **Исключение из Git** - личные данные не попадают в репозиторий
- **Миграция готова** для PostgreSQL/MongoDB

## 🌐 Развертывание

### Railway (рекомендуется)
```bash
npm install -g @railway/cli
railway login
railway new
railway up
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### VPS
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git
git clone https://github.com/yourusername/tarot-fortune-bot.git
cd tarot-fortune-bot
python3 -m venv tarot_bot_env
source tarot_bot_env/bin/activate
pip install -r requirements.txt
# Настроить .env
python main.py
```

## 🧪 Разработка

### Установка для разработки:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # pytest, black, flake8
```

### Запуск тестов:
```bash
pytest tests/
```

### Форматирование кода:
```bash
black bot/
flake8 bot/
```

### Добавление новой команды:
1. Создать обработчик в `bot/handlers/`
2. Зарегистрировать в `bot/bot.py`
3. Добавить в README и help

## 📈 Мониторинг

### Логи:
```bash
tail -f logs/bot.log
```

### Метрики:
- Количество пользователей: `/adminstats`
- Использование AI: логи уровня INFO
- Ошибки: логи уровня ERROR

## 🤝 Вклад в проект

1. Fork репозитория
2. Создать feature branch: `git checkout -b feature/amazing-feature`
3. Commit изменений: `git commit -m 'Add amazing feature'`
4. Push в branch: `git push origin feature/amazing-feature`
5. Открыть Pull Request

### Правила:
- Используйте type hints
- Покрывайте код тестами
- Следуйте PEP 8
- Обновляйте документацию

## 📝 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

### Что это означает:
- ✅ **Максимальная свобода** - используйте, модифицируйте, распространяйте как хотите
- ✅ **Коммерческое использование** - можете создавать платные версии
- ✅ **Любые форки** - открытые, закрытые, корпоративные
- ✅ **Простота** - никаких юридических сложностей
- ✅ **Совместимость** - объединяйте с любыми другими проектами

MIT выбрана для максимальной доступности и простоты использования проекта.

## 🙏 Благодарности

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - отличная библиотека для Telegram ботов
- [Groq](https://groq.com/) - быстрый AI провайдер для генерации толкований
- [Waite-Smith Tarot](https://en.wikipedia.org/wiki/Rider%E2%80%93Waite_tarot_deck) - классическая колода Таро

## 📞 Поддержка

- 🐛 [Issues](https://github.com/miakunin/tarot-fortune-bot/issues) - для багов и предложений
- 💬 [Discussions](https://github.com/miakunin/tarot-fortune-bot/discussions) - для вопросов

---

**⭐ Если проект понравился, поставьте звезду на GitHub!**

Сделано с ❤️  и магией карт Таро 🔮
