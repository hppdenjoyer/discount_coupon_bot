from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import INVITE_FRIEND, VIEW_PURCHASES, ADD_BALANCE
from models.user import get_user_profile

async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile button press."""
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)

    profile_text = f"""
👤 Ваш профиль:

ID: {user_id}
Баланс: {profile['balance']} руб.
Количество покупок: {profile['purchases_count']}
Приглашено друзей: {profile['invited_friends']}
    """

    keyboard = [
        [InlineKeyboardButton(text=INVITE_FRIEND, callback_data="profile_invite")],
        [InlineKeyboardButton(text=VIEW_PURCHASES, callback_data="profile_purchases")],
        [InlineKeyboardButton(text=ADD_BALANCE, callback_data="profile_balance")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(profile_text, reply_markup=reply_markup)

async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile-related callbacks."""
    query = update.callback_query
    await query.answer()

    action = query.data.replace("profile_", "")

    if action == "invite":
        invite_link = f"https://t.me/share/url?url=https://t.me/your_bot?start={update.effective_user.id}"
        await query.message.edit_text(
            "🎁 Пригласите друзей и получите бонус!\n\n"
            f"Ваша реферальная ссылка: {invite_link}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_profile")
            ]])
        )

    elif action == "purchases":
        purchases = get_user_profile(update.effective_user.id)['purchases']
        if not purchases:
            purchase_text = "У вас пока нет покупок."
        else:
            purchase_text = "Ваши последние покупки:\n\n"
            for purchase in purchases:
                purchase_text += f"🏷 {purchase['name']} - {purchase['date']}\n"

        await query.message.edit_text(
            purchase_text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_profile")
            ]])
        )

    elif action == "balance":
        await query.message.edit_text(
            "💰 Выберите сумму пополнения:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="100 ₽", callback_data="payment_100")],
                [InlineKeyboardButton(text="500 ₽", callback_data="payment_500")],
                [InlineKeyboardButton(text="1000 ₽", callback_data="payment_1000")],
                [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_profile")]
            ])
        )