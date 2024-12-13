from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL подключения к базе данных
DATABASE_URL = "postgresql+psycopg2://postgres:26Qr45TO@localhost:5432/tg_bot_db"

# Проверка соединения
try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("Соединение с базой данных успешно!")
    connection.close()
except Exception as e:
    print(f"Ошибка подключения: {e}")

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

if __name__ == "__main__":
    # Пример тестирования подключения
    session = create_db_connection()
    if session:
        session.close()



