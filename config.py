import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
TOKEN = os.getenv('BOT_TOKEN')

# Настройки администраторов
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

# Тексты кнопок
CATALOG_BUTTON = "🛍 Каталог"
PROFILE_BUTTON = "👤 Профиль"
RULES_BUTTON = "📜 Правила"
INVITE_FRIEND = "🎁 Пригласить друга"
VIEW_PURCHASES = "📋 Мои покупки"
ADD_BALANCE = "💰 Пополнить баланс"

# Текстовые сообщения
WELCOME_MESSAGE = """
Добро пожаловать в бот скидочных купонов! 🎉
Используйте меню для навигации.
"""

RULES_TEXT = """
📜 Правила использования бота:

1. Купоны действительны в течение указанного срока
2. Один купон можно использовать только один раз
3. Возврат средств не производится
4. При возникновении проблем обращайтесь в поддержку
"""

# Категории товаров
CATEGORIES = {
    "burgers": "🍔 Бургеры",
    "starters": "🥗 Стартеры",
    "drinks": "🥤 Напитки",
    "desserts": "🍰 Десерты"
}