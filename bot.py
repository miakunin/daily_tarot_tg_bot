import logging
import random
import os
import json
from datetime import datetime, date
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Импортировать колоду карт из отдельного файла
from tarot_cards import tarot_deck, fortune_templates, get_total_cards, get_cards_by_type

# Импорт для работы с Google Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google Generative AI не установлен. Используются статичные описания карт.")

# Загрузить переменные из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получить токены из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ADMIN_ID = os.getenv('ADMIN_ID')  # Ваш Telegram ID для админ команд

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Убедитесь, что он указан в .env файле")

# Настроить Gemini если доступен
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    USE_AI_INTERPRETATIONS = True
    print("🤖 Google Gemini API подключён - будут использоваться AI толкования")
else:
    USE_AI_INTERPRETATIONS = False
    if GEMINI_AVAILABLE:
        print("⚠️ GEMINI_API_KEY не найден в .env - используются статичные описания")

# Файл для хранения данных пользователей
USER_DATA_FILE = 'users_data.json'

async def generate_ai_interpretation(card_name, user_name=None):
    """Генерировать AI толкование карты Таро с помощью Google Gemini"""
    if not USE_AI_INTERPRETATIONS:
        return None
    
    try:
        # Создать персонализированный промпт
        user_part = f" для {user_name}" if user_name else ""
        
        prompt = f"""Ты мастер Таро с многолетним опытом. Создай персонализированное толкование карты "{card_name}"{user_part}.

Требования:
- Тон: мистический, мудрый, но доброжелательный
- Длина: 2-3 предложения
- Включи практический совет для сегодняшнего дня
- Используй красивые эмоджи (🌟✨🔮💫🌙)
- Пиши на русском языке
- Избегай негативных предсказаний, даже для "сложных" карт

Пример структуры: "🌟 [Краткое значение карты]. [Что это означает для сегодня]. ✨ [Практический совет]."

Карта: {card_name}

Ответь только толкованием, без дополнительных комментариев."""

        # Попробовать разные модели в порядке предпочтения
        models_to_try = [
            'gemini-2.0-flash',      # Новая быстрая модель
            'gemini-1.5-pro',       # Новая продвинутая модель  
            'gemini-pro',           # Старая модель (может не работать)
            'models/gemini-1.5-flash',  # С префиксом models/
            'models/gemini-1.5-pro'
        ]
        
        for model_name in models_to_try:
            try:
                # Использовать текущую модель
                model = genai.GenerativeModel(model_name)
                
                # Настройки генерации
                generation_config = genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=200,
                    top_p=0.9,
                    top_k=40
                )
                
                # Сгенерировать ответ
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if response.text:
                    interpretation = response.text.strip()
                    logger.info(f"Gemini AI толкование успешно сгенерировано для карты: {card_name} (модель: {model_name})")
                    return interpretation
                else:
                    logger.warning(f"Gemini модель {model_name} вернула пустой ответ")
                    continue
                    
            except Exception as model_error:
                logger.warning(f"Модель {model_name} не работает: {model_error}")
                continue
        
        # Если ни одна модель не сработала
        logger.error("Все модели Gemini недоступны")
        return None
        
    except Exception as e:
        error_msg = str(e)
        
        # Специальная обработка разных типов ошибок Gemini
        if "quota" in error_msg.lower() or "limit" in error_msg.lower():
            logger.warning("Gemini API: Превышена квота. Переключаемся на классические толкования.")
        elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            logger.error("Gemini API: Проблема с API ключом.")
        elif "safety" in error_msg.lower():
            logger.warning("Gemini API: Ответ заблокирован фильтрами безопасности.")
        elif "blocked" in error_msg.lower():
            logger.warning("Gemini API: Контент заблокирован. Используем классическое толкование.")
        elif "404" in error_msg or "not found" in error_msg.lower():
            logger.error("Gemini API: Модель не найдена. Обновите библиотеку: pip install --upgrade google-generativeai")
        else:
            logger.error(f"Ошибка Gemini API: {e}")
        
        # В любом случае возвращаем None для fallback на классические толкования
        return None

def generate_fortune(card, user_name=None):
    """Сгенерировать сообщение с предсказанием (статичное)"""
    template = random.choice(fortune_templates)
    return template.format(name=card['name'], meaning=card['meaning'])

async def generate_fortune_with_ai(card, user_name=None):
    """Сгенерировать предсказание с возможностью AI толкования"""
    # Попробовать получить AI толкование
    ai_interpretation = await generate_ai_interpretation(card['name'], user_name)
    
    if ai_interpretation:
        # Используем AI толкование
        ai_templates = [
            "🔮 Карта дня - **{name}**\n\n{ai_meaning}\n\n💫 Пусть это послание направляет вас сегодня!",
            "🌟 Вселенная открывает **{name}** для вас сегодня.\n\n{ai_meaning}\n\n🙏 Доверьтесь мудрости карт.",
            "✨ Карты заговорили! **{name}** несёт особое послание.\n\n{ai_meaning}\n\n🌙 Примите это руководство с открытым сердцем."
        ]
        template = random.choice(ai_templates)
        return template.format(name=card['name'], ai_meaning=ai_interpretation)
    else:
        # Fallback на статичное описание (без user_name, так как функция его не использует)
        return generate_fortune(card)

# Колода Таро импортируется из tarot_cards.py

def draw_random_card():
    """Вытянуть случайную карту из колоды"""
    return random.choice(tarot_deck)

def generate_fortune(card):
    """Сгенерировать сообщение с предсказанием"""
    template = random.choice(fortune_templates)
    return template.format(name=card['name'], meaning=card['meaning'])

def load_user_data():
    """Загрузить данные пользователей из файла"""
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        logger.error("Ошибка чтения файла пользователей")
        return {}

def save_user_data(data):
    """Сохранить данные пользователей в файл"""
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения данных пользователей: {e}")

def can_get_fortune(user_id):
    """Проверить, может ли пользователь получить предсказание сегодня"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str not in user_data:
        return True
    
    last_fortune_date = user_data[user_id_str].get('last_fortune_date')
    if not last_fortune_date:
        return True
    
    # Проверяем, что прошёл новый день
    today = date.today().isoformat()
    return last_fortune_date != today

def update_user_fortune_date(user_id):
    """Обновить дату последнего предсказания пользователя"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str not in user_data:
        user_data[user_id_str] = {}
    
    user_data[user_id_str]['last_fortune_date'] = date.today().isoformat()
    user_data[user_id_str]['total_fortunes'] = user_data[user_id_str].get('total_fortunes', 0) + 1
    
    save_user_data(user_data)

def get_user_stats(user_id):
    """Получить статистику пользователя"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str not in user_data:
        return {'total_fortunes': 0, 'last_fortune_date': None}
    
    return user_data[user_id_str]
    """Вытянуть случайную карту из колоды"""
    return random.choice(tarot_deck)

def generate_fortune(card):
    """Сгенерировать сообщение с предсказанием"""
    fortunes = [
        f"🔮 Карта дня - **{card['name']}**\n\n{card['meaning']}\n\n✨ Пусть это руководство осветит ваш путь сегодня!",
        f"🌟 Карты заговорили! **{card['name']}** появляется для вас сегодня.\n\n{card['meaning']}\n\n🙏 Примите мудрость этой карты.",
        f"🃏 Ваше ежедневное чтение Таро раскрывает **{card['name']}**\n\n{card['meaning']}\n\n💫 Пусть это послание направляет ваш день с целью.",
        f"✨ Вселенная представляет **{card['name']}** вам сегодня.\n\n{card['meaning']}\n\n🌙 Доверьтесь пути, который разворачивается перед вами."
    ]
    
    return random.choice(fortunes)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_name = update.effective_user.first_name or "друг"
    card_stats = get_cards_by_type()
    ai_status = "🤖 Gemini AI толкования" if USE_AI_INTERPRETATIONS else "📚 Классические"
    
    welcome_message = f"""
🔮 Добро пожаловать в бот Ежедневных Предсказаний Таро, {user_name}! 🔮

✨ Я даю только ОДНО предсказание в день - как настоящий мастер Таро.

🎴 **Моя колода содержит {card_stats['total']} карт:**
🔮 {card_stats['major_arcana']} Старших Арканов
⚔️ {card_stats['minor_arcana']} Младших Арканов (все 4 масти)

🧠 **Режим толкований:** {ai_status} 💰 БЕСПЛАТНО!

Команды:
/fortune - Получить своё ежедневное предсказание
/card - То же, что и /fortune
/stats - Посмотреть вашу статистику
/deck - Информация о колоде
/ai - Переключить режим толкований
/help - Показать справку

🌟 Готовы узнать, что уготовили вам карты сегодня? 
Используйте /fortune чтобы получить своё уникальное послание!

💫 Помните: карты дают мудрость лишь раз в день.
    """
    
    await update.message.reply_text(welcome_message)

async def check_available_models():
    """Проверить доступные модели Gemini"""
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        return []
    
    try:
        models = genai.list_models()
        available_models = []
        
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
        
        return available_models
    except Exception as e:
        logger.error(f"Ошибка получения списка моделей: {e}")
        return []

async def ai_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /status - статус AI системы"""
    if not GEMINI_AVAILABLE:
        status_message = """
❌ **Статус AI: Недоступен**

📦 Google Generative AI библиотека не установлена
💡 Для установки: `pip install --upgrade google-generativeai`
🔄 Используются классические толкования карт
        """
    elif not GEMINI_API_KEY:
        status_message = """
⚠️ **Статус AI: Не настроен**

🔑 GEMINI_API_KEY не найден в .env файле
🌐 Получите ключ на: https://makersuite.google.com/app/apikey
🔄 Используются классические толкования карт
        """
    else:
        # Попробуем сделать тестовый запрос
        test_result = await generate_ai_interpretation("Дурак", "тест")
        
        if test_result:
            # Получить список доступных моделей
            available_models = await check_available_models()
            models_text = "\n".join([f"  • {model}" for model in available_models[:5]])  # Показать первые 5
            if len(available_models) > 5:
                models_text += f"\n  • ... и ещё {len(available_models) - 5} моделей"
            
            status_message = f"""
✅ **Статус AI: Работает**

🤖 Google Gemini API подключён и функционирует
🔮 AI толкования: {"включены" if USE_AI_INTERPRETATIONS else "выключены"}
🎯 Активная модель: Gemini-1.5-Flash (приоритет)
✨ Персонализированные толкования доступны
💰 Бесплатный лимит: 60 запросов в минуту

📋 **Доступные модели:**
{models_text if models_text else "  • Загрузка..."}

💡 Используйте /ai чтобы переключить режим
            """
        else:
            status_message = """
❌ **Статус AI: Ошибка**

🔑 API ключ настроен, но есть проблемы:
• Модель gemini-pro больше не поддерживается
• Обновите библиотеку: pip install --upgrade google-generativeai
• Возможно, превышен лимит запросов (60/мин)
• Проблемы с сетью

🔄 Автоматически используются классические толкования
📊 Проверьте ключ на: https://makersuite.google.com/
            """
    
    await update.message.reply_text(status_message, parse_mode='Markdown')

async def ai_toggle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /ai - переключение режима толкований"""
    global USE_AI_INTERPRETATIONS
    
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        await update.message.reply_text(
            "❌ AI толкования недоступны.\n\n"
            "Для включения добавьте GEMINI_API_KEY в .env файл и установите: pip install google-generativeai"
        )
        return
    
    # Переключить режим
    USE_AI_INTERPRETATIONS = not USE_AI_INTERPRETATIONS
    
    status = "включены 🤖" if USE_AI_INTERPRETATIONS else "выключены 📚"
    mode = "персонализированные Gemini толкования" if USE_AI_INTERPRETATIONS else "классические описания карт"
    
    toggle_message = f"""
🔄 **Режим толкований изменён!**

✨ AI толкования: {status}
🎯 Текущий режим: {mode}

🤖 **Gemini толкования:** Уникальные, персонализированные интерпретации (БЕСПЛАТНО!)
📚 **Классические:** Традиционные значения карт Таро

💡 Используйте /ai чтобы снова переключить режим.
    """
    
    await update.message.reply_text(toggle_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    ai_status = "🤖 включены" if USE_AI_INTERPRETATIONS else "📚 выключены"
    ai_availability = "" if (GEMINI_AVAILABLE and GEMINI_API_KEY) else "\n❌ AI недоступны (нет Gemini API ключа)"
    
    help_message = f"""
🃏 **Команды бота Предсказаний Таро:**

/fortune - Получить ежедневное предсказание Таро
/card - То же, что и /fortune
/stats - Посмотреть вашу статистику  
/deck - Информация о колоде карт
/ai - Переключить режим толкований (AI/классические)
/status - Проверить статус AI системы
/start - Приветственное сообщение
/help - Показать эту справку

✨ **Особенности бота:**
🌙 Только одно предсказание в день на человека
🔮 Уникальные послания для каждого пользователя
📊 Статистика ваших обращений к картам
🎴 Полная колода из 78 карт Таро
🤖 Gemini AI толкования: {ai_status} (БЕСПЛАТНО!){ai_availability}

*Помните: чтения Таро предназначены для развлечения и самоанализа.*

💫 Пусть карты направляют ваш путь!
    """
    
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def deck_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /deck - информация о колоде"""
    card_stats = get_cards_by_type()
    
    deck_message = f"""
🃏 **Информация о колоде Таро:**

📊 **Статистика карт:**
🔮 Старшие Арканы: {card_stats['major_arcana']} карт
⚔️ Младшие Арканы: {card_stats['minor_arcana']} карт
🎴 Всего карт в колоде: {card_stats['total']} карт

🌟 **Младшие Арканы включают все четыре масти:**
💧 Кубки (Вода) - эмоции, отношения, духовность
🌍 Пентакли (Земля) - материальный мир, финансы, карьера  
💨 Мечи (Воздух) - мысли, конфликты, общение
🔥 Жезлы (Огонь) - действие, энергия, творчество

✨ Каждое предсказание уникально и выбирается случайным образом из полной колоды!
    """
    
    await update.message.reply_text(deck_message, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "друг"
    stats = get_user_stats(user_id)
    
    if stats.get('total_fortunes', 0) == 0:
        stats_message = f"""
📊 {user_name}, ваша статистика пока пуста...

🔮 Вы ещё не получали предсказаний от карт.
✨ Используйте /fortune чтобы получить своё первое послание!

💫 Пусть путешествие в мир Таро начнётся!
        """
    else:
        # Проверить, можно ли получить предсказание сегодня
        can_get_today = can_get_fortune(user_id)
        status = "✅ Доступно" if can_get_today else "⏳ Ждите до завтра"
        
        stats_message = f"""
📊 **Статистика {user_name}:**

🔮 Всего предсказаний: {stats.get('total_fortunes', 0)}
📅 Последнее предсказание: {stats.get('last_fortune_date', 'неизвестно')}
🌟 Сегодняшнее предсказание: {status}

✨ Каждое обращение к картам приближает вас к мудрости!
        """
    
    await update.message.reply_text(stats_message, parse_mode='Markdown')

async def fortune(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команд /fortune и /card"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "друг"
    
    # Проверить, может ли пользователь получить предсказание
    if not can_get_fortune(user_id):
        # Получить статистику пользователя
        stats = get_user_stats(user_id)
        
        waiting_message = f"""
🌙 {user_name}, карты уже открыли вам свои тайны сегодня...

✨ Вселенная дарует только одно предсказание в день. 
🕐 Возвращайтесь завтра, чтобы узнать, что готовят вам звёзды.

📊 Ваша статистика:
🔮 Всего предсказаний: {stats.get('total_fortunes', 0)}
📅 Последнее предсказание: {stats.get('last_fortune_date', 'неизвестно')}

💫 Пусть сегодняшнее послание направляет вас до завтрашнего рассвета!
        """
        
        await update.message.reply_text(waiting_message)
        return
    
    # Показать индикатор "печатает..." пока генерируется предсказание
    await update.message.reply_chat_action('typing')
    
    # Вытянуть случайную карту
    drawn_card = draw_random_card()
    
    # Обновить дату последнего предсказания
    update_user_fortune_date(user_id)
    
    # Сгенерировать сообщение с предсказанием (возможно с AI)
    fortune_message = await generate_fortune_with_ai(drawn_card, user_name)
    
    # Получить обновлённую статистику
    stats = get_user_stats(user_id)
    
    # Добавить информацию об источнике толкования
    source_info = "🤖 Персональное AI толкование" if USE_AI_INTERPRETATIONS else "📚 Классическое толкование"
    
    # Отправить предсказание с дополнительной информацией
    full_message = f"Привет, {user_name}! 🌟\n\n{fortune_message}\n\n"
    
    # Добавить особое сообщение для первого предсказания
    if stats.get('total_fortunes', 0) == 1:
        full_message += "🎉 Это ваше первое предсказание! Добро пожаловать в мир Таро!\n\n"
    else:
        full_message += f"📊 Это ваше {stats.get('total_fortunes', 0)}-е предсказание\n\n"
    
    full_message += f"{source_info}\n💫 Помните: новое предсказание будет доступно завтра!"
    
    await update.message.reply_text(full_message, parse_mode='Markdown')

async def admin_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /reset - сброс базы данных (только для админа)"""
    user_id = update.effective_user.id
    
    # Проверить права админа
    if ADMIN_ID and str(user_id) != str(ADMIN_ID):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Создать бэкап
        if os.path.exists(USER_DATA_FILE):
            backup_file = f"users_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import shutil
            shutil.copy(USER_DATA_FILE, backup_file)
            
            # Очистить базу данных
            os.remove(USER_DATA_FILE)
            
            reset_message = f"""
🔧 **База данных сброшена!**

✅ Старая база сохранена как: `{backup_file}`
🗑️ Активная база очищена
🔄 Все пользователи смогут получить новое предсказание

⚠️ Это действие необратимо!
            """
        else:
            reset_message = """
📝 **База данных уже пуста!**

✅ Файл users_data.json не существует
🔄 Все пользователи смогут получить предсказание
            """
        
        await update.message.reply_text(reset_message, parse_mode='Markdown')
        logger.info(f"База данных сброшена админом: {user_id}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка сброса базы данных: {e}")
        logger.error(f"Ошибка сброса БД: {e}")

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /adminstats - статистика бота (только для админа)"""
    user_id = update.effective_user.id
    
    # Проверить права админа
    if ADMIN_ID and str(user_id) != str(ADMIN_ID):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        user_data = load_user_data()
        total_users = len(user_data)
        total_fortunes = sum(user.get('total_fortunes', 0) for user in user_data.values())
        
        # Пользователи сегодня
        today = date.today().isoformat()
        users_today = sum(1 for user in user_data.values() 
                         if user.get('last_fortune_date') == today)
        
        stats_message = f"""
📊 **Статистика бота:**

👥 Всего пользователей: {total_users}
🔮 Всего предсказаний: {total_fortunes}
📅 Активных сегодня: {users_today}
🤖 AI толкования: {"включены" if USE_AI_INTERPRETATIONS else "выключены"}
🎴 Карт в колоде: {get_total_cards()}

⚙️ **Админ команды:**
/reset - сбросить базу данных
/adminstats - эта статистика
        """
        
        await update.message.reply_text(stats_message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка получения статистики: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик обычных сообщений"""
    user_name = update.effective_user.first_name or "друг"
    ai_status = "🤖 Gemini AI" if USE_AI_INTERPRETATIONS else "📚 классические"
    
    message = f"""
🔮 Привет, {user_name}! Я ваш бот Ежедневных Предсказаний Таро.

✨ Используйте /fortune чтобы получить своё ежедневное предсказание
📊 Используйте /stats чтобы посмотреть статистику
🎴 Используйте /deck чтобы узнать о колоде
🤖 Используйте /ai чтобы переключить режим толкований
🔧 Используйте /status чтобы проверить статус AI
❓ Используйте /help для всех команд

🧠 Текущий режим: {ai_status} толкования (БЕСПЛАТНО!)
🌟 Помните: карты дарят мудрость только раз в день!
    """
    
    await update.message.reply_text(message)

def main() -> None:
    """Запуск бота"""
    # Создать приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавить обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fortune", fortune))
    application.add_handler(CommandHandler("card", fortune))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("deck", deck_info_command))
    application.add_handler(CommandHandler("ai", ai_toggle_command))
    application.add_handler(CommandHandler("status", ai_status_command))
    
    # Админские команды
    application.add_handler(CommandHandler("reset", admin_reset_command))
    application.add_handler(CommandHandler("adminstats", admin_stats_command))
    
    # Добавить обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Информация о колоде при запуске
    card_stats = get_cards_by_type()
    ai_mode = "Gemini AI персонализированные" if USE_AI_INTERPRETATIONS else "классические статичные"
    ai_available = "✅ доступны (БЕСПЛАТНО)" if (GEMINI_AVAILABLE and GEMINI_API_KEY) else "❌ недоступны"
    admin_status = f"✅ настроен ({ADMIN_ID})" if ADMIN_ID else "❌ не настроен"
    
    # Запустить бота
    print("🔮 Бот Ежедневных Предсказаний Таро запущен...")
    print("✨ Система ограничений активна: одно предсказание в день!")
    print(f"🎴 Колода содержит: {card_stats['total']} карт ({card_stats['major_arcana']} старших + {card_stats['minor_arcana']} младших арканов)")
    print(f"🧠 Режим толкований: {ai_mode}")
    print(f"🤖 Gemini AI толкования: {ai_available}")
    print(f"👑 Админ доступ: {admin_status}")
    print("Используйте Ctrl+C чтобы остановить бота")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        print("🔮 Бот завершил работу")

if __name__ == '__main__':
    main()
