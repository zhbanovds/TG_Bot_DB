# bot.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import logging
from handlers import add_review, save_review, choose_delivery
from database.queries import get_all_products, add_order, get_user_by_telegram_id

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот, который поможет вам найти товары и оформить заказы. Используйте команды для взаимодействия!"
    )

# Команда /products для вывода списка продуктов
async def products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    products = get_all_products()
    if not products:
        await update.message.reply_text('В магазине пока нет товаров.')
        return

    keyboard = []
    for product in products:
        keyboard.append([InlineKeyboardButton(f"{product.name} - {product.price}$", callback_data=str(product.id))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Доступные товары:', reply_markup=reply_markup)

# Основная функция для запуска бота
def main() -> None:
    # Используйте ApplicationBuilder вместо Updater
    application = ApplicationBuilder().token("7646968433:AAEjNe1TK-n5YdoP9fejXUX7VJwcnl4eB3E").build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("products", products))
    application.add_handler(CallbackQueryHandler(add_review, pattern='^add_review$'))  # Обработка добавления отзыва
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_review))  # Сохранение текста отзыва

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()


