from telegram import ReplyKeyboardMarkup, KeyboardButton
from config import CATALOG_BUTTON, PROFILE_BUTTON, RULES_BUTTON

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = [
        [KeyboardButton(CATALOG_BUTTON), KeyboardButton(PROFILE_BUTTON)],
        [KeyboardButton(RULES_BUTTON)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)