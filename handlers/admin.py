from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Список ID администраторов
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь администратором."""
    return user_id in ADMIN_IDS

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /admin."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет прав администратора.")
        return

    keyboard = [
        [InlineKeyboardButton("➕ Добавить купон", callback_data="admin_add_coupon")],
        [InlineKeyboardButton("❌ Удалить купон", callback_data="admin_delete_coupon")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔐 Панель администратора\nВыберите действие:",
        reply_markup=reply_markup
    )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка callback запросов админ-панели."""
    query = update.callback_query
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await query.answer("У вас нет прав администратора.")
        return
    
    await query.answer()
    action = query.data.replace("admin_", "")

    if action == "add_coupon":
        context.user_data['admin_state'] = 'waiting_coupon_data'
        await query.message.edit_text(
            "Отправьте данные купона в формате:\n"
            "Категория\nНазвание\nЦена\nОписание\n\n"
            "Пример:\nburgers\nБургер Классический\n299\nВкусный бургер с котлетой"
        )
    
    elif action == "delete_coupon":
        # Загружаем список купонов для удаления
        try:
            with open('data/products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            keyboard = []
            for category, items in products.items():
                for item in items:
                    keyboard.append([InlineKeyboardButton(
                        f"❌ {item['name']} ({category})",
                        callback_data=f"delete_coupon_{item['id']}"
                    )])
            
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="admin_back")])
            await query.message.edit_text(
                "Выберите купон для удаления:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            await query.message.edit_text("Ошибка при загрузке списка купонов")
    
    elif action == "stats":
        # Подсчет статистики
        try:
            with open('data/products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            with open('data/users.json', 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            total_products = sum(len(cat) for cat in products.values())
            total_users = len(users)
            total_purchases = sum(user.get('purchases_count', 0) for user in users.values())
            
            stats_text = (
                "📊 Статистика бота:\n\n"
                f"Купонов в системе: {total_products}\n"
                f"Пользователей: {total_users}\n"
                f"Всего покупок: {total_purchases}"
            )
            
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="admin_back")]]
            await query.message.edit_text(
                stats_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            await query.message.edit_text("Ошибка при подсчете статистики")

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений в режиме администратора."""
    if not is_admin(update.effective_user.id):
        return
    
    if context.user_data.get('admin_state') == 'waiting_coupon_data':
        try:
            # Парсинг данных купона
            category, name, price, description = update.message.text.strip().split('\n')
            price = float(price)
            
            # Генерация ID для купона
            from uuid import uuid4
            coupon_id = str(uuid4())[:8]
            
            # Загрузка существующих купонов
            products_file = Path('data/products.json')
            if products_file.exists():
                with open(products_file, 'r', encoding='utf-8') as f:
                    products = json.load(f)
            else:
                products = {}
            
            # Добавление новой категории, если её нет
            if category not in products:
                products[category] = []
            
            # Добавление нового купона
            new_coupon = {
                "id": coupon_id,
                "name": name,
                "price": price,
                "description": description,
                "category": category
            }
            products[category].append(new_coupon)
            
            # Сохранение обновленных данных
            with open(products_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=4)
            
            await update.message.reply_text(
                f"✅ Купон успешно добавлен!\n\n"
                f"ID: {coupon_id}\n"
                f"Категория: {category}\n"
                f"Название: {name}\n"
                f"Цена: {price} руб.\n"
                f"Описание: {description}"
            )
            
            # Сброс состояния
            context.user_data.pop('admin_state', None)
            
        except ValueError as e:
            await update.message.reply_text(
                "❌ Ошибка в формате данных.\n"
                "Используйте формат:\n"
                "Категория\nНазвание\nЦена\nОписание"
            )
        except Exception as e:
            logger.error(f"Error adding coupon: {e}")
            await update.message.reply_text("❌ Произошла ошибка при добавлении купона")
