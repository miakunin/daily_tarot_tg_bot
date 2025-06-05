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

# Загрузить переменные из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получить токен из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Убедитесь, что он указан в .env файле")

# Файл для хранения данных пользователей
USER_DATA_FILE = 'data/users_data.json'

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
    
    welcome_message = f"""
🔮 Добро пожаловать в бот Ежедневных Предсказаний Таро, {user_name}! 🔮

✨ Я даю только ОДНО предсказание в день - как настоящий мастер Таро.

🎴 **Моя колода содержит {card_stats['total']} карт:**
🔮 {card_stats['major_arcana']} Старших Арканов
⚔️ {card_stats['minor_arcana']} Младших Арканов (все 4 масти)

Команды:
/fortune - Получить своё ежедневное предсказание
/card - То же, что и /fortune
/stats - Посмотреть вашу статистику
/deck - Информация о колоде
/help - Показать справку

🌟 Готовы узнать, что уготовили вам карты сегодня? 
Используйте /fortune чтобы получить своё уникальное послание!

💫 Помните: карты дают мудрость лишь раз в день.
    """
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_message = """
🃏 **Команды бота Предсказаний Таро:**

/fortune - Получить ежедневное предсказание Таро
/card - То же, что и /fortune
/stats - Посмотреть вашу статистику  
/deck - Информация о колоде карт
/start - Приветственное сообщение
/help - Показать эту справку

✨ **Особенности бота:**
🌙 Только одно предсказание в день на человека
🔮 Уникальные послания для каждого пользователя
📊 Статистика ваших обращений к картам
🎴 Полная колода из 78 карт Таро

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
    
    # Вытянуть случайную карту
    drawn_card = draw_random_card()
    
    # Обновить дату последнего предсказания
    update_user_fortune_date(user_id)
    
    # Сгенерировать сообщение с предсказанием
    fortune_message = generate_fortune(drawn_card)
    
    # Получить обновлённую статистику
    stats = get_user_stats(user_id)
    
    # Отправить предсказание с дополнительной информацией
    full_message = f"Привет, {user_name}! 🌟\n\n{fortune_message}\n\n"
    
    # Добавить особое сообщение для первого предсказания
    if stats.get('total_fortunes', 0) == 1:
        full_message += "🎉 Это ваше первое предсказание! Добро пожаловать в мир Таро!\n\n"
    else:
        full_message += f"📊 Это ваше {stats.get('total_fortunes', 0)}-е предсказание\n\n"
    
    full_message += "💫 Помните: новое предсказание будет доступно завтра!"
    
    await update.message.reply_text(full_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик обычных сообщений"""
    user_name = update.effective_user.first_name or "друг"
    message = f"""
🔮 Привет, {user_name}! Я ваш бот Ежедневных Предсказаний Таро.

✨ Используйте /fortune чтобы получить своё ежедневное предсказание
📊 Используйте /stats чтобы посмотреть статистику
🎴 Используйте /deck чтобы узнать о колоде
❓ Используйте /help для всех команд

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
    
    # Добавить обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Информация о колоде при запуске
    card_stats = get_cards_by_type()
    
    # Запустить бота
    print("🔮 Бот Ежедневных Предсказаний Таро запущен...")
    print("✨ Система ограничений активна: одно предсказание в день!")
    print(f"🎴 Колода содержит: {card_stats['total']} карт ({card_stats['major_arcana']} старших + {card_stats['minor_arcana']} младших арканов)")
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
