from telegram import Update
from telegram.ext import ContextTypes
from config import RULES_TEXT

async def handle_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle rules button press."""
    await update.message.reply_text(RULES_TEXT)
