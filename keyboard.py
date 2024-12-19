from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для выбора между регистрацией и авторизацией
def auth_or_register_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Регистрация")],
            [KeyboardButton(text="Авторизация")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# Основное меню после авторизации/регистрации пользователя
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Аккаунт пользователя")],
            [KeyboardButton(text="Каталог товаров")],
            [KeyboardButton(text="Корзина")]
        ],
        resize_keyboard=True
    )

# Клавиатура для раздела "Аккаунт пользователя"
def account_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Данные пользователя")],
            [KeyboardButton(text="Мои заказы")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

# Клавиатура для товаров в каталоге
def catalog_item_keyboard(product_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart:{product_id}")]
        ]
    )

# Общая кнопка "Назад" для каталога
def catalog_back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

# Клавиатура для раздела "Корзина"
def cart_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")],
            [InlineKeyboardButton(text="Удалить товар", callback_data="remove_item")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
        ]
    )

# Клавиатура для подтверждения оформления заказа
def confirm_checkout_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data="confirm_order")],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel_order")]
        ]
    )

# Клавиатура для возврата к главному меню
def back_to_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Назад в меню")]
        ],
        resize_keyboard=True
    )
