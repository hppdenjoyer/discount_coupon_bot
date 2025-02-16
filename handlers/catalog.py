from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import CATEGORIES
import json

async def handle_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle catalog button press."""
    keyboard = []
    for category_id, category_name in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(
            text=category_name, 
            callback_data=f"category_{category_id}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Выберите категорию:",
        reply_markup=reply_markup
    )

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection."""
    query = update.callback_query
    await query.answer()

    category_id = query.data.replace("category_", "")

    # Load products from JSON
    with open('data/products.json', 'r', encoding='utf-8') as file:
        products = json.load(file)

    category_products = products.get(category_id, [])
    if not category_products:
        await query.message.edit_text("В данной категории пока нет товаров.")
        return

    # Create product list with buy buttons
    keyboard = []
    products_text = f"📋 {CATEGORIES[category_id]}:\n\n"

    for product in category_products:
        products_text += f"🏷 {product['name']}\n"
        products_text += f"💰 Цена: {product['price']} руб.\n"
        products_text += f"📝 {product['description']}\n\n"
        keyboard.append([InlineKeyboardButton(
            text=f"Купить {product['name']}", 
            callback_data=f"buy_{product['id']}"
        )])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_categories")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        products_text,
        reply_markup=reply_markup
    )