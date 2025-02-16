import os

# Bot configuration
TOKEN = os.getenv('TOKEN')  # Using environment variable for token

# Menu text
WELCOME_MESSAGE = "Добро пожаловать в магазин купонов со скидками! 🎉"
RULES_TEXT = """
Правила использования бота:
1. Купоны действительны в течение указанного срока
2. Возврат средств осуществляется в течение 24 часов
3. Один купон можно использовать только один раз
4. При возникновении проблем обращайтесь в поддержку
"""

# Keyboard buttons
CATALOG_BUTTON = "🛍 Каталог"
PROFILE_BUTTON = "👤 Профиль"
RULES_BUTTON = "📜 Правила"

# Categories
CATEGORIES = {
    "burgers": "🍔 Бургеры",
    "starters": "🥗 Стартеры",
    "drinks": "🥤 Напитки",
    "desserts": "🍰 Десерты"
}

# Profile options
INVITE_FRIEND = "👥 Пригласить друга"
VIEW_PURCHASES = "📋 Мои покупки"
ADD_BALANCE = "⭐️ Пополнить баланс"