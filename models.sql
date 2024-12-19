-- Таблица Users
CREATE TABLE IF NOT EXISTS Users (
    id BIGINT PRIMARY KEY, -- Telegram ID
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(20) DEFAULT 'customer'
);

-- Таблица Customers
CREATE TABLE IF NOT EXISTS Customers (
    id BIGINT PRIMARY KEY REFERENCES Users(id), -- Telegram ID
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL, -- Синхронизирован с Users.email
    phone VARCHAR(20)
);

-- Таблица Categories
CREATE TABLE IF NOT EXISTS Categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE
);

-- Таблица Products
CREATE TABLE IF NOT EXISTS Products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    brand VARCHAR(50),
    size VARCHAR(10),
    price NUMERIC(10, 2),
    category_id INTEGER REFERENCES Categories(id),
    stock_quantity INTEGER
);

-- Таблица Orders
CREATE TABLE IF NOT EXISTS Orders (
    id SERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES Customers(id), -- Telegram ID
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pending',
    total_amount NUMERIC(10, 2)
);

-- Таблица Order_Items
CREATE TABLE IF NOT EXISTS Order_Items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES Orders(id),
    product_id INTEGER REFERENCES Products(id),
    quantity INTEGER,
    price NUMERIC(10, 2)
);

-- Таблица Cart
CREATE TABLE IF NOT EXISTS Cart (
    id SERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES Customers(id), -- Telegram ID
    product_id INTEGER REFERENCES Products(id),
    quantity INTEGER,
    CONSTRAINT unique_customer_product UNIQUE (customer_id, product_id)
);

-- Первичное заполнение таблицы Categories
INSERT INTO Categories (name) VALUES
('Одежда'),
('Обувь'),
('Аксессуары')
ON CONFLICT DO NOTHING;

-- Первичное заполнение таблицы Products
INSERT INTO Products (name, brand, size, price, category_id, stock_quantity) VALUES
('Футболка Polo', 'Ralph Lauren', 'M', 75.00, 1, 20),
('Джинсы Slim Fit', 'Levi’s', '32', 120.00, 1, 15),
('Кроссовки Air Max', 'Nike', '42', 150.00, 2, 10),
('Сумка Tote', 'Michael Kors', '-', 200.00, 3, 5),
('Ремень Кожаный', 'Tommy Hilfiger', '-', 50.00, 3, 25)
ON CONFLICT DO NOTHING;
