# db_config.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# URL подключения к базе данных (для примера используется SQLite)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///my_database.db")

# Создаем объект движка для подключения к базе данных
engine = create_engine(DATABASE_URL, echo=True)

# Создаем фабрику для создания сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_connection():
    """
    Функция для создания подключения к базе данных.
    Возвращает объект сессии для работы с базой данных.
    """
    try:
        db_session = SessionLocal()
        print("Подключение к базе данных успешно создано.")
        return db_session
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None
