from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import ContextTypes
from models.user import get_user_profile, update_user_profile
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process payment using Telegram Payments"""
    query = update.callback_query
    await query.answer()

    amount = int(query.data.replace("payment_", ""))
    user_id = update.effective_user.id

    try:
        provider_token = os.getenv('TELEGRAM_PAYMENT_TOKEN')
        logger.info(f"Payment request initiated - User: {user_id}, Amount: {amount} RUB")

        if not provider_token:
            logger.error("Payment provider token not configured")
            raise ValueError("Payment provider token not configured")

        # Create the price with proper formatting
        prices = [LabeledPrice(label=f"Пополнение баланса ({amount} ₽)", amount=amount * 100)]  # Amount in kopecks

        # Build a unique payload with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        payload = f"balance_topup_{amount}_{timestamp}_{user_id}"

        logger.info(f"Sending invoice with payload: {payload}")

        await context.bot.send_invoice(
            chat_id=user_id,
            title=f"Пополнение баланса на {amount} ₽",
            description="Пополнение баланса в боте для покупки купонов со скидками",
            payload=payload,
            provider_token=provider_token,
            currency="RUB",
            prices=prices,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False,
            protect_content=True
        )

        await query.message.edit_text(
            "💳 Оплата\n"
            "Для завершения оплаты, пожалуйста, следуйте инструкциям в платежном окне.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_profile")
            ]])
        )
        logger.info(f"Payment invoice sent successfully to user {user_id}")

    except Exception as e:
        logger.error(f"Payment error for user {user_id}: {str(e)}")
        error_message = "Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."

        if "Bad Request" in str(e):
            if "provider_token" in str(e).lower():
                error_message = "Ошибка платежного токена. Пожалуйста, обратитесь к администратору."
                logger.error("Invalid provider token detected")
            else:
                logger.error(f"Bad request error details: {str(e)}")

        await query.message.edit_text(
            error_message,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_profile")
            ]])
        )

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment"""
    payment = update.message.successful_payment
    amount = payment.total_amount / 100  # Convert from kopecks to rubles
    user_id = update.effective_user.id

    logger.info(f"Processing successful payment - User: {user_id}, Amount: {amount} RUB, "
               f"Payload: {payment.invoice_payload}")

    try:
        # Update user balance
        user_profile = get_user_profile(user_id)
        previous_balance = user_profile['balance']
        user_profile['balance'] += amount
        update_user_profile(user_id, user_profile)

        logger.info(f"Balance updated successfully - User: {user_id}, "
                   f"Previous: {previous_balance} RUB, New: {user_profile['balance']} RUB")

        await update.message.reply_text(
            f"✅ Платеж успешно обработан!\n\n"
            f"Сумма: {amount} ₽\n"
            f"Предыдущий баланс: {previous_balance} ₽\n"
            f"Текущий баланс: {user_profile['balance']} ₽"
        )
    except Exception as e:
        logger.error(f"Error updating balance - User: {user_id}, Error: {str(e)}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обновлении баланса.\n"
            "Пожалуйста, обратитесь в поддержку и сохраните ID платежа."
        )