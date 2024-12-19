import psycopg2
import logging
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logging.basicConfig(
    filename="errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            self.connection.autocommit = True
        except Exception as e:
            logging.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def fetch_data(self, query, parameters=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, parameters)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка выполнения SELECT-запроса: {query} | Ошибка: {e}")
            raise

    def execute_query(self, query, parameters=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, parameters)
        except Exception as e:
            logging.error(f"Ошибка выполнения SQL-запроса: {query} | Ошибка: {e}")
            raise

    def get_customer_data_by_email(self, email):
        query = "SELECT name, email, phone FROM Customers WHERE email = %s"
        try:
            result = self.fetch_data(query, (email,))
            return result[0] if result else None
        except Exception as e:
            logging.error(f"Ошибка получения данных клиента по email {email}: {e}")
            raise

    def add_new_user_and_customer(self, telegram_id, username, password_hash, name, email, phone):
        """
        Добавление нового пользователя в таблицу Users и соответствующего клиента в таблицу Customers.
        """
        try:
            # Добавление пользователя в Users
            user_query = "INSERT INTO Users (id, username, email, password_hash) VALUES (%s, %s, %s, %s)"
            self.execute_query(user_query, (telegram_id, username, email, password_hash))

            # Добавление клиента в Customers
            customer_query = "INSERT INTO Customers (id, name, email, phone) VALUES (%s, %s, %s, %s)"
            self.execute_query(customer_query, (telegram_id, name, email, phone))
        except Exception as e:
            logging.error(f"Ошибка добавления пользователя {username} и клиента {email}: {e}")
            raise

    def email_exists(self, email):
        """
        Проверить существование email в таблице Users.
        :param email: Email для проверки.
        :return: True, если email существует, иначе False.
        """
        query = "SELECT COUNT(*) FROM Users WHERE email = %s"
        try:
            result = self.fetch_data(query, (email,))
            return result[0][0] > 0
        except Exception as e:
            logging.error(f"Ошибка проверки существования email {email}: {e}")
            raise

    def get_password_hash(self, email):
        """
        Получить хэш пароля по email из таблицы Users.
        """
        query = "SELECT password_hash FROM Users WHERE email = %s"
        try:
            result = self.fetch_data(query, (email,))
            return result[0][0] if result else None
        except Exception as e:
            logging.error(f"Ошибка получения хэша пароля для email {email}: {e}")
            raise

    def add_to_cart(self, telegram_id, product_id, quantity=1):
        """
        Добавление товара в корзину (Cart).
        Если товар уже есть в корзине, увеличивает количество.
        """
        query = """
        INSERT INTO Cart (customer_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON CONFLICT (customer_id, product_id) DO UPDATE SET quantity = Cart.quantity + EXCLUDED.quantity;
        """
        try:
            self.execute_query(query, (telegram_id, product_id, quantity))
        except Exception as e:
            logging.error(f"Ошибка добавления товара {product_id} в корзину для пользователя {telegram_id}: {e}")
            raise

    def get_cart_items(self, telegram_id):
        """
        Получение товаров из корзины пользователя.
        """
        query = """
        SELECT p.name, c.quantity, p.price, (c.quantity * p.price) AS total_price
        FROM Cart c
        JOIN Products p ON c.product_id = p.id
        WHERE c.customer_id = %s
        """
        try:
            return self.fetch_data(query, (telegram_id,))
        except Exception as e:
            logging.error(f"Ошибка получения товаров из корзины пользователя {telegram_id}: {e}")
            raise

    def create_order(self, telegram_id, total_amount):
        """
        Создание заказа для пользователя.
        """
        query = "INSERT INTO Orders (customer_id, total_amount) VALUES (%s, %s) RETURNING id"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (telegram_id, total_amount))
                return cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"Ошибка создания заказа для пользователя {telegram_id}: {e}")
            raise

    def add_order_item(self, order_id, product_id, quantity, price):
        query = """
        INSERT INTO Order_Items (order_id, product_id, quantity, price)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.execute_query(query, (order_id, product_id, quantity, price))
        except Exception as e:
            logging.error(f"Ошибка добавления позиции заказа order_id={order_id}, product_id={product_id}: {e}")
            raise

    def update_stock_quantity(self, product_id, quantity_change):
        query = """
        UPDATE Products
        SET stock_quantity = stock_quantity + %s
        WHERE id = %s
        """
        try:
            self.execute_query(query, (quantity_change, product_id))
        except Exception as e:
            logging.error(f"Ошибка обновления количества на складе для product_id={product_id}: {e}")
            raise

    def clear_cart(self, customer_id):
        query = "DELETE FROM Cart WHERE customer_id = %s"
        try:
            self.execute_query(query, (customer_id,))
        except Exception as e:
            logging.error(f"Ошибка очистки корзины для customer_id={customer_id}: {e}")
            raise
    def get_customer_orders(self, customer_id):
        query = """
        SELECT id, order_date, status, total_amount
        FROM Orders
        WHERE customer_id = %s
        ORDER BY order_date DESC
        """
        try:
            return self.fetch_data(query, (customer_id,))
        except Exception as e:
            logging.error(f"Ошибка получения заказов для клиента {customer_id}: {e}")
            raise


