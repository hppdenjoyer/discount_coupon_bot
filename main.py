import logging
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    filters,
)
from handlers.commands import start, help_command
from handlers.catalog import handle_catalog, category_callback
from handlers.profile import handle_profile, profile_callback
from handlers.rules import handle_rules
from handlers.payment import process_payment, successful_payment
from config import TOKEN
from handlers.admin import admin_command, admin_callback, handle_admin_message

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.error(f'Update "{update}" caused error "{context.error}"')
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )

async def precheckout_callback(update: Update, context: Application.context_types) -> None:
    """Handles pre-checkout callbacks"""
    query = update.pre_checkout_query
    logger.info(f"Processing pre-checkout query: {query.invoice_payload}")

    try:
        # Always approve pre-checkout queries in this simple implementation
        await query.answer(ok=True)
        logger.info("Pre-checkout query approved")
    except Exception as e:
        logger.error(f"Error in pre-checkout: {str(e)}")
        await query.answer(ok=False, error_message="Ошибка обработки платежа")

def main():
    """Start the bot."""
    try:
        # Create application
        application = Application.builder().token(TOKEN).build()
        logger.info("Starting bot in polling mode")

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("admin", admin_command))  # New admin command

        # Message handlers
        application.add_handler(MessageHandler(
            filters.Regex('^🛍 Каталог$'), handle_catalog))
        application.add_handler(MessageHandler(
            filters.Regex('^👤 Профиль$'), handle_profile))
        application.add_handler(MessageHandler(
            filters.Regex('^📜 Правила$'), handle_rules))

        # Admin message handler
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, handle_admin_message))

        # Payment handlers
        application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
        application.add_handler(MessageHandler(
            filters.SUCCESSFUL_PAYMENT, successful_payment))

        # Callback query handlers
        application.add_handler(CallbackQueryHandler(
            category_callback, pattern='^category_'))
        application.add_handler(CallbackQueryHandler(
            profile_callback, pattern='^profile_'))
        application.add_handler(CallbackQueryHandler(
            process_payment, pattern='^payment_'))
        application.add_handler(CallbackQueryHandler(
            admin_callback, pattern='^admin_'))  # New admin callback handler

        # Error handler
        application.add_error_handler(error_handler)

        # Start the bot
        application.run_polling()

    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")

if __name__ == '__main__':
    main()