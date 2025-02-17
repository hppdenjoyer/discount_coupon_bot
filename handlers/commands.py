from aiogram import Router, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from config import WELCOME_MESSAGE, CATALOG_BUTTON, PROFILE_BUTTON, RULES_BUTTON
from utils.keyboard import get_main_keyboard

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    """Отправка приветственного сообщения и основной клавиатуры при команде /start."""
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def help_command(message: Message):
    """Отправка справочного сообщения при команде /help."""
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /help - Показать это сообщение

    Используйте кнопки меню для навигации:
    🛍 Каталог - Просмотр доступных купонов
    👤 Профиль - Управление профилем
    📜 Правила - Правила использования
    """
    await message.answer(help_text)

def register_command_handlers(dp: Dispatcher):
    """Регистрация обработчиков базовых команд."""
    dp.include_router(router)
