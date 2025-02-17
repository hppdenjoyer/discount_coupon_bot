from aiogram import Router, F, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import INVITE_FRIEND, VIEW_PURCHASES, ADD_BALANCE
from models.user import get_user_profile

router = Router()

@router.message(F.text == "👤 Профиль")
async def handle_profile(message: Message):
    """Обработка нажатия кнопки профиля."""
    await show_profile(message)

@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(query: CallbackQuery):
    """Обработка возврата в профиль."""
    await query.answer()
    await show_profile(query.message, edit=True)

async def show_profile(message: Message, edit: bool = False):
    """Показ профиля пользователя."""
    user_id = message.chat.id if isinstance(message, Message) else message.chat.id
    profile = get_user_profile(user_id)

    profile_text = f"""
👤 Ваш профиль:

ID: {user_id}
Баланс: {profile['balance']} руб.
Количество покупок: {profile['purchases_count']}
Приглашено друзей: {profile['invited_friends']}
    """

    builder = InlineKeyboardBuilder()
    builder.button(text=INVITE_FRIEND, callback_data="profile_invite")
    builder.button(text=VIEW_PURCHASES, callback_data="profile_purchases")
    builder.button(text=ADD_BALANCE, callback_data="profile_balance")
    builder.adjust(1)

    if edit:
        await message.edit_text(profile_text, reply_markup=builder.as_markup())
    else:
        await message.answer(profile_text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("profile_"))
async def profile_callback(query: CallbackQuery):
    """Обработка callback-запросов профиля."""
    await query.answer()
    action = query.data.replace("profile_", "")

    if action == "invite":
        # Формирование реферальной ссылки
        invite_link = f"https://t.me/share/url?url=https://t.me/your_bot?start={query.from_user.id}"
        builder = InlineKeyboardBuilder()
        builder.button(text="◀️ Назад", callback_data="back_to_profile")

        await query.message.edit_text(
            "🎁 Пригласите друзей и получите бонус!\n\n"
            f"Ваша реферальная ссылка: {invite_link}",
            reply_markup=builder.as_markup()
        )

    elif action == "purchases":
        # Отображение истории покупок
        purchases = get_user_profile(query.from_user.id)['purchases']
        if not purchases:
            purchase_text = "У вас пока нет покупок."
        else:
            purchase_text = "Ваши последние покупки:\n\n"
            for purchase in purchases:
                purchase_text += f"🏷 {purchase['name']} - {purchase['date']}\n"

        builder = InlineKeyboardBuilder()
        builder.button(text="◀️ Назад", callback_data="back_to_profile")

        await query.message.edit_text(
            purchase_text,
            reply_markup=builder.as_markup()
        )

    elif action == "balance":
        # Меню пополнения баланса
        builder = InlineKeyboardBuilder()
        builder.button(text="100 ₽", callback_data="payment_100")
        builder.button(text="500 ₽", callback_data="payment_500")
        builder.button(text="1000 ₽", callback_data="payment_1000")
        builder.button(text="◀️ Назад", callback_data="back_to_profile")
        builder.adjust(1)

        await query.message.edit_text(
            "💰 Выберите сумму пополнения:",
            reply_markup=builder.as_markup()
        )

def register_profile_handlers(dp: Dispatcher):
    """Регистрация обработчиков профиля."""
    dp.include_router(router)