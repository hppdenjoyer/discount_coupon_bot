from aiogram import Router, F
from aiogram.types import Message
from config import RULES_TEXT

router = Router()

@router.message(F.text == "📜 Правила")
async def handle_rules(message: Message):
    """Обработка нажатия кнопки правил."""
    await message.answer(RULES_TEXT)

def register_rules_handlers(dp):
    """Регистрация обработчиков правил."""
    dp.include_router(router)
