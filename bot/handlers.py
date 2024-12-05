# handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler, filters
from database.db_config import create_db_connection
from database.init_db import Order, Review, Delivery, Product, User
from sqlalchemy.orm import Session
import logging
import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация базы данных
session: Session = create_db_connection()

# Обработка создания заказа
def create_order(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    product_id = int(query.data)

    # Получаем информацию о пользователе и продукте
    user_telegram_id = update.effective_user.id
    user = session.query(User).filter(User.id == user_telegram_id).first()
    product = session.query(Product).filter(Product.id == product_id).first()

    if not user:
        query.edit_message_text(text="Для оформления заказа необходимо зарегистрироваться.")
        return

    if product:
        new_order = Order(
            user_id=user.id,
            product_id=product.id,
            order_date=datetime.datetime.now(),
            status="В обработке",
            total_amount=product.price
        )
        session.add(new_order)
        session.commit()
        query.edit_message_text(text=f"Ваш заказ на товар '{product.name}' успешно создан и находится в обработке.")
    else:
        query.edit_message_text(text="Ошибка при создании заказа. Попробуйте позже.")

# Обработка добавления отзыва
def add_review(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    product_id = int(query.data)

    user_telegram_id = update.effective_user.id
    user = session.query(User).filter(User.id == user_telegram_id).first()

    if not user:
        query.edit_message_text(text="Для оставления отзыва необходимо зарегистрироваться.")
        return

    context.user_data['review_product_id'] = product_id
    query.edit_message_text(text="Пожалуйста, отправьте ваш отзыв текстом.")

# Сохранение текста отзыва
def save_review(update: Update, context: CallbackContext) -> None:
    user_telegram_id = update.effective_user.id
    product_id = context.user_data.get('review_product_id')
    review_text = update.message.text

    if product_id:
        new_review = Review(
            user_id=user_telegram_id,
            product_id=product_id,
            review_text=review_text,
            rating=5  # Здесь можно добавить функционал для выбора рейтинга
        )
        session.add(new_review)
        session.commit()
        update.message.reply_text("Спасибо за ваш отзыв!")
    else:
        update.message.reply_text("Ошибка при сохранении отзыва. Попробуйте позже.")

# Функция для обработки доставки
def choose_delivery(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("Доставка курьером", callback_data='courier')],
        [InlineKeyboardButton("Самовывоз", callback_data='pickup')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите способ доставки:", reply_markup=reply_markup)


