from aiogram import Router, F, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CATEGORIES
from models.user import get_user_profile, update_user_profile
import json
import logging
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "🛍 Каталог")
async def handle_catalog(message: Message):
    """Обработка нажатия кнопки каталога."""
    await show_categories(message)

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(query: CallbackQuery):
    """Обработка возврата к списку категорий."""
    await query.answer()
    await show_categories(query.message, edit=True)

async def show_categories(message: Message, edit: bool = False):
    """Показ списка категорий."""
    builder = InlineKeyboardBuilder()

    for category_id, category_name in CATEGORIES.items():
        builder.button(
            text=category_name,
            callback_data=f"category_{category_id}"
        )
    builder.adjust(1)

    text = "Выберите категорию:"
    if edit:
        await message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("category_"))
async def category_callback(query: CallbackQuery):
    """Обработка выбора категории."""
    await query.answer()
    category_id = query.data.replace("category_", "")

    try:
        # Загрузка продуктов из JSON
        with open('data/products.json', 'r', encoding='utf-8') as file:
            products = json.load(file)

        category_products = products.get(category_id, [])
        if not category_products:
            await query.message.edit_text(
                "В данной категории пока нет товаров."
            )
            return

        builder = InlineKeyboardBuilder()
        products_text = f"📋 {CATEGORIES[category_id]}:\n\n"

        # Формирование списка продуктов с кнопками покупки
        for product in category_products:
            products_text += (
                f"🏷 {product['name']}\n"
                f"💰 Цена: {product['price']} руб.\n"
                f"📝 {product['description']}\n\n"
            )
            builder.button(
                text=f"Купить {product['name']}",
                callback_data=f"buy_{product['id']}"
            )

        builder.button(text="◀️ Назад", callback_data="back_to_categories")
        builder.adjust(1)

        await query.message.edit_text(
            products_text,
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка при загрузке товаров: {e}")
        await query.message.edit_text(
            "Произошла ошибка при загрузке товаров."
        )

@router.callback_query(F.data.startswith("buy_"))
async def buy_product(query: CallbackQuery):
    """Обработка нажатия кнопки покупки товара."""
    await query.answer()
    product_id = query.data.replace("buy_", "")

    try:
        # Поиск товара по ID
        with open('data/products.json', 'r', encoding='utf-8') as file:
            products = json.load(file)

        product = None
        for category in products.values():
            for item in category:
                if item['id'] == product_id:
                    product = item
                    break
            if product:
                break

        if not product:
            await query.message.edit_text(
                "Товар не найден. Возможно, он был удален.",
                reply_markup=InlineKeyboardBuilder()
                .button(text="◀️ Назад к категориям", callback_data="back_to_categories")
                .as_markup()
            )
            return

        # Формирование сообщения подтверждения покупки
        confirmation_text = (
            f"🛍 Подтверждение покупки:\n\n"
            f"Товар: {product['name']}\n"
            f"Цена: {product['price']} руб.\n\n"
            f"Вы уверены, что хотите купить этот товар?"
        )

        builder = InlineKeyboardBuilder()
        builder.button(
            text="✅ Подтвердить",
            callback_data=f"confirm_buy_{product_id}"
        )
        builder.button(
            text="❌ Отменить",
            callback_data=f"category_{product['category']}"
        )
        builder.adjust(2)

        await query.message.edit_text(
            confirmation_text,
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке покупки: {e}")
        await query.message.edit_text(
            "Произошла ошибка при обработке покупки.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="◀️ Назад к категориям", callback_data="back_to_categories")
            .as_markup()
        )

@router.callback_query(F.data.startswith("confirm_buy_"))
async def confirm_buy_product(query: CallbackQuery):
    """Обработка подтверждения покупки товара."""
    await query.answer()
    product_id = query.data.replace("confirm_buy_", "")
    user_id = query.from_user.id

    try:
        # Получаем профиль пользователя
        user_profile = get_user_profile(user_id)

        # Поиск товара по ID
        with open('data/products.json', 'r', encoding='utf-8') as file:
            products = json.load(file)

        product = None
        for category in products.values():
            for item in category:
                if item['id'] == product_id:
                    product = item
                    break
            if product:
                break

        if not product:
            await query.message.edit_text(
                "Товар не найден. Возможно, он был удален.",
                reply_markup=InlineKeyboardBuilder()
                .button(text="◀️ Назад к категориям", callback_data="back_to_categories")
                .as_markup()
            )
            return

        # Проверка баланса
        if user_profile['balance'] < product['price']:
            await query.message.edit_text(
                f"❌ Недостаточно средств!\n\n"
                f"Стоимость товара: {product['price']} руб.\n"
                f"Ваш баланс: {user_profile['balance']} руб.\n\n"
                f"Пополните баланс в разделе Профиль.",
                reply_markup=InlineKeyboardBuilder()
                .button(text="◀️ Назад к категориям", callback_data="back_to_categories")
                .as_markup()
            )
            return

        # Списание средств
        user_profile['balance'] -= product['price']
        user_profile['purchases_count'] += 1

        # Добавление покупки в историю
        purchase = {
            'id': product_id,
            'name': product['name'],
            'price': product['price'],
            'date': datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        user_profile['purchases'].append(purchase)

        # Сохранение обновленного профиля
        update_user_profile(user_id, user_profile)

        # Отправка сообщения об успешной покупке
        success_message = (
            f"✅ Покупка успешно совершена!\n\n"
            f"Товар: {product['name']}\n"
            f"Цена: {product['price']} руб.\n"
            f"Дата: {purchase['date']}\n\n"
            f"Текущий баланс: {user_profile['balance']} руб."
        )

        builder = InlineKeyboardBuilder()
        builder.button(text="◀️ К категориям", callback_data="back_to_categories")
        builder.button(text="👤 В профиль", callback_data="profile_purchases")
        builder.adjust(1)

        await query.message.edit_text(
            success_message,
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        logger.error(f"Ошибка при подтверждении покупки: {e}")
        await query.message.edit_text(
            "Произошла ошибка при обработке покупки.",
            reply_markup=InlineKeyboardBuilder()
            .button(text="◀️ Назад к категориям", callback_data="back_to_categories")
            .as_markup()
        )

def register_catalog_handlers(dp: Dispatcher):
    """Регистрация обработчиков каталога."""
    dp.include_router(router)