# queries.py

from sqlalchemy.orm import Session
from database.db_config import create_db_connection
from database.init_db import Product, User, Order, Review, Delivery
import datetime

# Инициализация базы данных
session: Session = create_db_connection()

# Получение всех продуктов
def get_all_products() -> list:
    try:
        products = session.query(Product).all()
        return products
    except Exception as e:
        print(f"Ошибка при получении продуктов: {e}")
        return []

# Получение пользователя по Telegram ID
def get_user_by_telegram_id(telegram_id: int) -> User:
    try:
        user = session.query(User).filter(User.id == telegram_id).first()
        return user
    except Exception as e:
        print(f"Ошибка при получении пользователя: {e}")
        return None

# Добавление нового заказа
def add_order(user_id: int, product_id: int, total_amount: float) -> bool:
    try:
        new_order = Order(
            user_id=user_id,
            product_id=product_id,
            order_date=datetime.datetime.now(),
            status="В обработке",
            total_amount=total_amount
        )
        session.add(new_order)
        session.commit()
        return True
    except Exception as e:
        print(f"Ошибка при добавлении заказа: {e}")
        session.rollback()
        return False

# Добавление отзыва
def add_review(user_id: int, product_id: int, review_text: str, rating: int = 5) -> bool:
    try:
        new_review = Review(
            user_id=user_id,
            product_id=product_id,
            review_text=review_text,
            rating=rating
        )
        session.add(new_review)
        session.commit()
        return True
    except Exception as e:
        print(f"Ошибка при добавлении отзыва: {e}")
        session.rollback()
        return False

# Получение всех заказов пользователя
def get_user_orders(user_id: int) -> list:
    try:
        orders = session.query(Order).filter(Order.user_id == user_id).all()
        return orders
    except Exception as e:
        print(f"Ошибка при получении заказов пользователя: {e}")
        return []

