from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
import os
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from bot_logic import BotLogic
from keyboard import (
    main_menu_keyboard,
    account_menu_keyboard,
    cart_menu_keyboard,  # Предполагается, что здесь вы обновили cart_menu_keyboard
    confirm_checkout_keyboard,
    back_to_main_keyboard,
    auth_or_register_keyboard,
    catalog_item_keyboard,
    catalog_back_keyboard
)
import logging

logging.basicConfig(level=logging.DEBUG)

router = Router()

db = Database()
db.connect()
bot_logic = BotLogic(db)

# Хранилище авторизованных пользователей в памяти: {user_id: email}
authorized_users = {}

class AuthStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()
    waiting_for_phone = State()
    waiting_for_password = State()

def generate_cart_keyboard(items):
    """
    Клавиатура для списка товаров в корзине при удалении.
    items: [(product_name, quantity, price, total_price, product_id), ...]
    """
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    for item in items:
        product_name, quantity, price, total_price, product_id = item
        button = InlineKeyboardButton(
            text=f"{product_name} ({quantity} шт.)",
            callback_data=f"confirm_remove:{product_id}"
        )
        # Добавляем новый ряд с одной кнопкой
        markup.inline_keyboard.append([button])

    return markup

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=auth_or_register_keyboard()
    )

@router.message(F.text == "Регистрация")
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Введите ваше имя для регистрации:")
    await state.set_state(RegistrationStates.waiting_for_name)

@router.message(RegistrationStates.waiting_for_name)
async def process_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Введите ваш email:")
    await state.set_state(RegistrationStates.waiting_for_email)

@router.message(RegistrationStates.waiting_for_email)
async def process_email(msg: Message, state: FSMContext):
    email = msg.text.strip()
    if bot_logic.email_exists(email):
        await msg.answer("Этот email уже зарегистрирован. Попробуйте авторизоваться.")
        await state.clear()
        return
    await state.update_data(email=email)
    await msg.answer("Введите ваш номер телефона:")
    await state.set_state(RegistrationStates.waiting_for_phone)

@router.message(RegistrationStates.waiting_for_phone)
async def process_phone(msg: Message, state: FSMContext):
    await state.update_data(phone=msg.text)
    await msg.answer("Введите ваш пароль:")
    await state.set_state(RegistrationStates.waiting_for_password)

@router.message(RegistrationStates.waiting_for_password)
async def process_password(msg: Message, state: FSMContext):
    registration_data = await state.get_data()
    hashed_password = bot_logic.hash_password(msg.text)
    db.add_new_user_and_customer(
        telegram_id=msg.from_user.id,
        username=registration_data["email"],
        password_hash=hashed_password,
        name=registration_data["name"],
        email=registration_data["email"],
        phone=registration_data["phone"]
    )
    authorized_users[msg.from_user.id] = registration_data["email"]
    await state.clear()
    await msg.answer("Регистрация завершена!", reply_markup=main_menu_keyboard())

@router.message(F.text == "Авторизация")
async def start_authorization(message: Message, state: FSMContext):
    await message.answer("Введите ваш email:")
    await state.set_state(AuthStates.waiting_for_email)

@router.message(AuthStates.waiting_for_email)
async def process_auth_email(msg: Message, state: FSMContext):
    email = msg.text.strip()
    if not bot_logic.email_exists(email):
        await msg.answer("Этот email не зарегистрирован. Пожалуйста, зарегистрируйтесь.")
        await state.clear()
        return
    await state.update_data(auth_email=email)
    await msg.answer("Введите ваш пароль:")
    await state.set_state(AuthStates.waiting_for_password)

@router.message(AuthStates.waiting_for_password)
async def process_auth_password(msg: Message, state: FSMContext):
    data = await state.get_data()
    email = data["auth_email"]
    password = msg.text.strip()
    if bot_logic.check_authorization(email, password):
        authorized_users[msg.from_user.id] = email
        await state.clear()
        await msg.answer("Авторизация успешна!", reply_markup=main_menu_keyboard())
    else:
        await msg.answer("Неверный email или пароль.")
        await state.clear()

@router.message(F.text == "Аккаунт пользователя")
async def account_menu(message: Message):
    await message.answer("Выберите действие:", reply_markup=account_menu_keyboard())

@router.message(F.text == "Данные пользователя")
async def user_data(message: Message):
    email = authorized_users.get(message.from_user.id)
    if not email:
        await message.answer("Вы не авторизованы. Пожалуйста, авторизуйтесь.")
        return

    customer_info = db.get_customer_data_by_email(email)
    if customer_info:
        name, customer_email, phone = customer_info
        response = f"Ваши данные:\nИмя: {name}\nEmail: {customer_email}\nТелефон: {phone}"
    else:
        response = "Информация о вас не найдена. Вы зарегистрированы?"
    await message.answer(response)

@router.message(F.text == "Мои заказы")
async def my_orders(message: Message):
    orders = bot_logic.get_customer_orders(message.from_user.id)
    if orders:
        response = "Ваши заказы:\n"
        for order in orders:
            order_id, order_date, status, total_amount = order
            response += f"Заказ №{order_id} от {order_date.date()} на сумму {total_amount} руб., статус: {status}\n"
    else:
        response = "У вас ещё нет заказов."
    await message.answer(response)

@router.message(F.text == "Каталог товаров")
async def catalog_menu(message: Message):
    products = db.fetch_data("SELECT id, name, brand, size, price FROM Products")
    if products:
        for product in products:
            product_id = product[0]
            product_info = (
                f"Название: {product[1]}\n"
                f"Бренд: {product[2]}\n"
                f"Размер: {product[3]}\n"
                f"Цена: {product[4]} руб."
            )
            image_path = os.path.join("images", f"{product_id}.png")
            if os.path.exists(image_path):
                photo = FSInputFile(image_path)
                await message.answer_photo(photo, caption=product_info, reply_markup=catalog_item_keyboard(product_id))
            else:
                await message.answer(product_info, reply_markup=catalog_item_keyboard(product_id))

        await message.answer("Выберите следующее действие:", reply_markup=catalog_back_keyboard())
    else:
        await message.answer("К сожалению, товаров нет.", reply_markup=main_menu_keyboard())

@router.message(F.text == "Корзина")
async def cart_menu(message: Message):
    customer_id = message.from_user.id
    cart_items = db.get_cart_items(customer_id)
    if cart_items:
        response = "Ваши товары в корзине:\n"
        total = 0
        for item in cart_items:
            response += f"{item[0]} - {item[1]} шт. по {item[2]} руб. (Итого: {item[3]} руб.)\n"
            total += item[3]
        response += f"\nОбщая сумма: {total} руб."
        await message.answer(response, reply_markup=cart_menu_keyboard())
    else:
        await message.answer("Ваша корзина пуста.", reply_markup=main_menu_keyboard())

@router.callback_query(F.data.startswith("add_to_cart"))
async def add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split(':')[1])
    customer_id = callback.from_user.id
    try:
        product = db.fetch_data("SELECT name FROM Products WHERE id = %s", (product_id,))
        if not product:
            await callback.message.answer("Ошибка: товар не найден.")
            await callback.answer()
            return
        product_name = product[0][0]
        db.add_to_cart(customer_id, product_id, 1)
        await callback.message.answer(f"Товар '{product_name}' добавлен в корзину!")
    except Exception as e:
        logging.error(f"Ошибка при добавлении товара в корзину: {e}")
        await callback.message.answer("Произошла ошибка при добавлении товара в корзину. Пожалуйста, попробуйте позже.")
    await callback.answer()

@router.callback_query(F.data == "remove_item")
async def remove_item_callback(callback: CallbackQuery):
    customer_id = callback.from_user.id
    cart_items = db.fetch_data(
        """
        SELECT p.name, c.quantity, p.price, (c.quantity * p.price) AS total_price, p.id
        FROM Cart c
        JOIN Products p ON c.product_id = p.id
        WHERE c.customer_id = %s
        """, (customer_id,)
    )
    if cart_items:
        await callback.message.edit_text(
            "Выберите товар для удаления:",
            reply_markup=generate_cart_keyboard(cart_items)
        )
    else:
        await callback.message.edit_text("Ваша корзина пуста.")
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_remove"))
async def confirm_remove_callback(callback: CallbackQuery):
    customer_id = callback.from_user.id
    product_id = int(callback.data.split(":")[1])
    db.execute_query(
        "DELETE FROM Cart WHERE customer_id = %s AND product_id = %s",
        (customer_id, product_id)
    )
    cart_items = db.fetch_data(
        """
        SELECT p.name, c.quantity, p.price, (c.quantity * p.price) AS total_price, p.id
        FROM Cart c
        JOIN Products p ON c.product_id = p.id
        WHERE c.customer_id = %s
        """, (customer_id,)
    )
    if cart_items:
        response = "Ваши товары в корзине:\n"
        total = 0
        for item in cart_items:
            product_name, quantity, price, total_price, prod_id = item
            response += f"{product_name} - {quantity} шт. по {price} руб. (Итого: {total_price} руб.)\n"
            total += total_price
        response += f"\nОбщая сумма: {total} руб."
        await callback.message.edit_text(response, reply_markup=cart_menu_keyboard())
    else:
        await callback.message.edit_text("Ваша корзина пуста.", reply_markup=main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "remove_all")
async def remove_all_items_callback(callback: CallbackQuery):
    customer_id = callback.from_user.id
    db.execute_query("DELETE FROM Cart WHERE customer_id = %s", (customer_id,))
    await callback.message.edit_text("Ваша корзина пуста.", reply_markup=main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    await callback.message.answer(
        "Подтвердите оформление заказа:",
        reply_markup=confirm_checkout_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery):
    customer_id = callback.from_user.id
    items = db.fetch_data(
        """
        SELECT product_id, quantity, price
        FROM Cart
        JOIN Products ON Cart.product_id = Products.id
        WHERE customer_id = %s
        """, (customer_id,)
    )
    if items:
        order_id = bot_logic.create_new_order(customer_id, items)
        await callback.message.answer(
            f"Ваш заказ успешно оформлен! Номер заказа: {order_id}",
            reply_markup=back_to_main_keyboard()
        )
    else:
        await callback.message.answer("Ваша корзина пуста.", reply_markup=main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery):
    await callback.message.answer("Оформление заказа отменено.", reply_markup=main_menu_keyboard())
    await callback.answer()

@router.message(F.text == "Назад")
async def back_to_main(message: Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu_keyboard())

@router.message(F.text == "Назад в меню")
async def back_to_main_menu(message: Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu_keyboard())
