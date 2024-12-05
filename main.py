# main.py

# Импорт необходимых модулей
from bot.bot import run_bot
from database.db_config import create_db_connection


def main():
    # Создаем подключение к базе данных
    db_connection = create_db_connection()

    # Запуск бота
    run_bot(db_connection)


if __name__ == "__main__":
    main()
