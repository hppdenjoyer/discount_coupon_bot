from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config import WELCOME_MESSAGE, CATALOG_BUTTON, PROFILE_BUTTON, RULES_BUTTON
from utils.keyboard import get_main_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message and main keyboard on /start command."""
    keyboard = get_main_keyboard()
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message when /help command is issued."""
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /help - Показать это сообщение
    
    Используйте кнопки меню для навигации:
    🛍 Каталог - Просмотр доступных купонов
    👤 Профиль - Управление профилем
    📜 Правила - Правила использования
    """
    await update.message.reply_text(help_text)
