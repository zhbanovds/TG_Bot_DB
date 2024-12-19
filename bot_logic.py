# bot_logic.py
import logging

logging.basicConfig(
    filename="errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BotLogic:
    def __init__(self, database):
        self.db = database

    def get_product_info(self, product_id):
        try:
            return self.db.fetch_data("SELECT * FROM Products WHERE id = %s", (product_id,))
        except Exception as e:
            logging.error(f"Ошибка получения информации о продукте с ID {product_id}: {e}")
            raise

    def email_exists(self, email):
        try:
            return self.db.fetch_data("SELECT COUNT(*) FROM Users WHERE username = %s", (email,))[0][0] > 0
        except Exception as e:
            logging.error(f"Ошибка проверки email {email}: {e}")
            raise

    def create_new_order(self, customer_id, items):
        """
        Создать новый заказ для клиента.
        :param customer_id: ID клиента.
        :param items: Список товаров (product_id, quantity, price).
        :return: ID созданного заказа.
        """
        try:
            total_amount = sum(item[1] * item[2] for item in items)  # Считаем общую сумму заказа
            order_id = self.db.create_order(customer_id, total_amount)

            for product_id, quantity, price in items:
                self.db.add_order_item(order_id, product_id, quantity, price)
                self.db.update_stock_quantity(product_id, -quantity)

            self.db.clear_cart(customer_id)  # Очищаем корзину клиента
            return order_id
        except Exception as e:
            logging.error(f"Ошибка создания нового заказа для клиента {customer_id}: {e}")
            raise

    def get_customer_orders(self, customer_id):
        try:
            return self.db.get_customer_orders(customer_id)
        except Exception as e:
            logging.error(f"Ошибка получения заказов клиента с ID {customer_id}: {e}")
            raise

    def register_customer(self, customer_id, name, email, phone, password_hash):
        """
        Зарегистрировать нового клиента.
        :param customer_id: ID клиента (Telegram ID).
        :param name: Имя клиента.
        :param email: Email клиента.
        :param phone: Номер телефона клиента.
        :param password_hash: Хэш пароля клиента.
        """
        try:
            self.db.add_new_customer(name, email, phone)
            self.db.add_new_user(email, password_hash)
        except Exception as e:
            logging.error(f"Ошибка регистрации клиента {customer_id}: {e}")
            raise

    def check_authorization(self, email, password):
        """
        Проверить авторизацию клиента.
        :param email: Email клиента.
        :param password: Пароль клиента.
        :return: True, если авторизация успешна, иначе False.
        """
        try:
            stored_hash = self.db.get_password_hash(email)
            return self.verify_password(password, stored_hash)
        except Exception as e:
            logging.error(f"Ошибка авторизации для email {email}: {e}")
            return False

    @staticmethod
    def hash_password(password):
        """
        Хэшировать пароль.
        :param password: Пароль для хэширования.
        :return: Хэшированный пароль.
        """
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, hashed):
        """
        Проверить пароль.
        :param password: Пароль для проверки.
        :param hashed: Хэш для сравнения.
        :return: True, если пароль совпадает, иначе False.
        """
        return BotLogic.hash_password(password) == hashed
