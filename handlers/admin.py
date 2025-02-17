from aiogram import Router, F, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
import os
from pathlib import Path
import logging
from utils.keyboard import get_admin_keyboard

router = Router()
logger = logging.getLogger(__name__)

# Admin states
class AdminStates(StatesGroup):
    waiting_coupon_data = State()

# Admin IDs list
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь администратором."""
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_command(message: Message):
    """Обработка команды /admin."""
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора.")
        return

    await message.answer(
        "🔐 Панель администратора\nВыберите действие:",
        reply_markup=get_admin_keyboard()
    )

@router.callback_query(F.data.startswith("admin_"))
async def admin_callback(query: CallbackQuery, state: FSMContext):
    """Обработка callback-запросов панели администратора."""
    if not is_admin(query.from_user.id):
        await query.answer("У вас нет прав администратора.")
        return

    await query.answer()
    action = query.data.replace("admin_", "")

    if action == "add_coupon":
        await state.set_state(AdminStates.waiting_coupon_data)
        await query.message.edit_text(
            "Отправьте данные купона в формате:\n"
            "Категория\nНазвание\nЦена\nОписание\n\n"
            "Пример:\nburgers\nБургер Классический\n299\nВкусный бургер"
        )

    elif action == "delete_coupon":
        try:
            with open('data/products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)

            builder = InlineKeyboardBuilder()
            for category, items in products.items():
                for item in items:
                    builder.button(
                        text=f"❌ {item['name']} ({category})",
                        callback_data=f"delete_coupon_{item['id']}"
                    )

            builder.button(text="◀️ Назад", callback_data="admin_back")
            builder.adjust(1)

            await query.message.edit_text(
                "Выберите купон для удаления:",
                reply_markup=builder.as_markup()
            )
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            await query.message.edit_text("Ошибка при загрузке списка купонов")

    elif action == "stats":
        try:
            with open('data/products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            with open('data/users.json', 'r', encoding='utf-8') as f:
                users = json.load(f)

            total_products = sum(len(cat) for cat in products.values())
            total_users = len(users)
            total_purchases = sum(
                user.get('purchases_count', 0) for user in users.values()
            )

            stats_text = (
                "📊 Статистика бота:\n\n"
                f"Купонов в системе: {total_products}\n"
                f"Пользователей: {total_users}\n"
                f"Всего покупок: {total_purchases}"
            )

            builder = InlineKeyboardBuilder()
            builder.button(text="◀️ Назад", callback_data="admin_back")

            await query.message.edit_text(
                stats_text,
                reply_markup=builder.as_markup()
            )
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            await query.message.edit_text("Ошибка при подсчете статистики")

@router.message(AdminStates.waiting_coupon_data)
async def handle_admin_message(message: Message, state: FSMContext):
    """Обработка сообщений администратора при ожидании данных купона."""
    if not is_admin(message.from_user.id):
        return

    try:
        # Parse coupon data
        category, name, price, description = message.text.strip().split('\n')
        price = float(price)

        # Generate coupon ID
        from uuid import uuid4
        coupon_id = str(uuid4())[:8]

        # Load existing products
        products_file = Path('data/products.json')
        if products_file.exists():
            with open(products_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
        else:
            products = {}

        # Add new category if it doesn't exist
        if category not in products:
            products[category] = []

        # Add new coupon
        new_coupon = {
            "id": coupon_id,
            "name": name,
            "price": price,
            "description": description,
            "category": category
        }
        products[category].append(new_coupon)

        # Save updated data
        with open(products_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)

        await message.answer(
            f"✅ Купон успешно добавлен!\n\n"
            f"ID: {coupon_id}\n"
            f"Категория: {category}\n"
            f"Название: {name}\n"
            f"Цена: {price} руб.\n"
            f"Описание: {description}"
        )

        # Reset state
        await state.clear()

    except ValueError:
        await message.answer(
            "❌ Ошибка в формате данных.\n"
            "Используйте формат:\n"
            "Категория\nНазвание\nЦена\nОписание"
        )
    except Exception as e:
        logger.error(f"Error adding coupon: {e}")
        await message.answer("❌ Произошла ошибка при добавлении купона")

def register_admin_handlers(dp: Dispatcher):
    """Регистрация обработчиков администратора."""
    dp.include_router(router)
