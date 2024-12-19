# Настройки бота
BOT_TOKEN = "7646968433:AAEjNe1TK-n5YdoP9fejXUX7VJwcnl4eB3E"  # Укажите токен вашего Telegram-бота

# Настройки подключения к базе данных PostgreSQL
DB_HOST = "localhost"          # Хост базы данных
DB_PORT = "5432"               # Порт базы данных
DB_NAME = "tg_bot_db"            # Имя базы данных
DB_USER = "postgres"           # Имя пользователя базы данных
DB_PASSWORD = "26Qr45TO"     # Пароль пользователя базы данных

# Проверка на корректность конфигурации
if not BOT_TOKEN:
    raise ValueError("Токен бота не установлен. Пожалуйста, задайте BOT_TOKEN.")
if not DB_USER or not DB_PASSWORD:
    raise ValueError("Настройки базы данных не установлены. Проверьте параметры подключения.")
