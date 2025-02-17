from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from config import CATALOG_BUTTON, PROFILE_BUTTON, RULES_BUTTON


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Получение основной клавиатуры меню."""
    keyboard = [
        [
            KeyboardButton(text=CATALOG_BUTTON),
            KeyboardButton(text=PROFILE_BUTTON)
        ],
        [KeyboardButton(text=RULES_BUTTON)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Получение клавиатуры панели администратора."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Добавить купон",
                callback_data="admin_add_coupon"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Удалить купон",
                callback_data="admin_delete_coupon"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin_stats"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)