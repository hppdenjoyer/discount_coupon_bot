from aiogram import Router, F, Dispatcher
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.user import get_user_profile, update_user_profile
import os
import logging
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith("payment_"))
async def process_payment(query: CallbackQuery):
    """Обработка платежа через Telegram Payments."""
    await query.answer()
    amount = int(query.data.replace("payment_", ""))
    user_id = query.from_user.id

    try:
        provider_token = os.getenv('TELEGRAM_PAYMENT_TOKEN')
        logger.info(f"Инициирован запрос на оплату - Пользователь: {user_id}, Сумма: {amount} РУБ")

        if not provider_token:
            logger.error("Не настроен токен платежной системы")
            raise ValueError("Не настроен токен платежной системы")

        # Создание цены с правильным форматированием
        prices = [LabeledPrice(label=f"Пополнение баланса ({amount} ₽)", amount=amount * 100)]  # Сумма в копейках

        # Формирование уникального payload с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        payload = f"balance_topup_{amount}_{timestamp}_{user_id}"

        logger.info(f"Отправка счета с payload: {payload}")

        await query.message.answer_invoice(
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

        builder = InlineKeyboardBuilder()
        builder.button(text="◀️ Назад", callback_data="back_to_profile")

        await query.message.edit_text(
            "💳 Оплата\n"
            "Для завершения оплаты, пожалуйста, следуйте инструкциям в платежном окне.",
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        logger.error(f"Ошибка платежа для пользователя {user_id}: {str(e)}")
        error_message = "Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."

        if "Bad Request" in str(e):
            if "provider_token" in str(e).lower():
                error_message = "Ошибка платежного токена. Пожалуйста, обратитесь к администратору."
                logger.error("Обнаружен недействительный токен провайдера")
            else:
                logger.error(f"Детали ошибки Bad Request: {str(e)}")

        builder = InlineKeyboardBuilder()
        builder.button(text="◀️ Назад", callback_data="back_to_profile")

        await query.message.edit_text(
            error_message,
            reply_markup=builder.as_markup()
        )

@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout: PreCheckoutQuery):
    """Обработка пре-чекаута."""
    await pre_checkout.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message):
    """Обработка успешного платежа."""
    payment = message.successful_payment
    amount = payment.total_amount / 100  # Конвертация из копеек в рубли
    user_id = message.from_user.id

    logger.info(f"Обработка успешного платежа - Пользователь: {user_id}, Сумма: {amount} РУБ, "
               f"Payload: {payment.invoice_payload}")

    try:
        # Обновление баланса пользователя
        user_profile = get_user_profile(user_id)
        previous_balance = user_profile['balance']
        user_profile['balance'] += amount
        update_user_profile(user_id, user_profile)

        logger.info(f"Баланс успешно обновлен - Пользователь: {user_id}, "
                   f"Предыдущий: {previous_balance} РУБ, Новый: {user_profile['balance']} РУБ")

        await message.answer(
            f"✅ Платеж успешно обработан!\n\n"
            f"Сумма: {amount} ₽\n"
            f"Предыдущий баланс: {previous_balance} ₽\n"
            f"Текущий баланс: {user_profile['balance']} ₽"
        )
    except Exception as e:
        logger.error(f"Ошибка обновления баланса - Пользователь: {user_id}, Ошибка: {str(e)}")
        await message.answer(
            "❌ Произошла ошибка при обновлении баланса.\n"
            "Пожалуйста, обратитесь в поддержку и сохраните ID платежа."
        )

def register_payment_handlers(dp: Dispatcher):
    """Регистрация обработчиков платежей."""
    dp.include_router(router)