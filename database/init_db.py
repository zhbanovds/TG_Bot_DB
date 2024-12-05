# init_db.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from database.db_config import engine


Base = declarative_base()

# Определение моделей базы данных

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Float)
    size = Column(String)
    color = Column(String)
    stock_quantity = Column(Integer)

    category = relationship("Category", back_populates="products")
    discounts = relationship("Discount", secondary="discount_products", back_populates="products")
    reviews = relationship("Review", back_populates="product")
    orders = relationship("Order", back_populates="product")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_info = Column(String)
    purchase_history = Column(String)

    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    order_date = Column(DateTime)
    status = Column(String)
    total_amount = Column(Float)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"))

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    delivery = relationship("Delivery", back_populates="orders")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    products = relationship("Product", back_populates="category")

class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    discount_rate = Column(Float)

    products = relationship("Product", secondary="discount_products", back_populates="discounts")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    review_text = Column(String)
    rating = Column(Integer)

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    status = Column(String)
    shipping_date = Column(DateTime)

    orders = relationship("Order", back_populates="delivery")

# Таблица для связи скидок и продуктов
from sqlalchemy import Table

discount_products = Table(
    'discount_products', Base.metadata,
    Column('discount_id', Integer, ForeignKey('discounts.id')),
    Column('product_id', Integer, ForeignKey('products.id'))
)

# Функция инициализации базы данных
def init_db():
    """
    Функция для создания всех таблиц в базе данных.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("База данных успешно инициализирована.")
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")

# Запуск инициализации, если файл запускается напрямую
if __name__ == "__main__":
    init_db()
