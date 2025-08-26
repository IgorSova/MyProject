"""
Модуль, содержащий классы и методы работы с БД
"""
import sqlite3 as sql
import pandas as pd
import datetime as dt
import random
def CreateDatabase():
    """
    Создает БД с таблицами:
        Orders:
            order_id (int) - уникальный номер заказа
            date - дата создания заказа
            customer_id - номер клиента, сделавшего заказ
        Customers:
            customer_id (int) - уникальный номер клиента
            name (str) - имя (название) клиента
            contact (str) - контакт (номер телефона или email) клиента
            address (str) - адрес доставки для клиента
        Goods:
            good_id (int) - уникальный номер товара
            good (str) - наименование товара
            price (float) - цена единицы товара
        Order_details:
            detail_id (int) - уникальный номер строки
            order_id (int) - уникальный номер заказа
            good_id (int) - уникальный номер товара в заказе
            quantity (int) - количество единиц товара в заказе
    """
    conn = sql.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS Customers 
                (
                    customer_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    address TEXT NOT NULL
                )
                ''')
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS Goods 
                (
                    good_id INTEGER PRIMARY KEY,
                    good TEXT NOT NULL,
                    price REAL
                )
                ''')
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS Orders 
                (
                    order_id INTEGER PRIMARY KEY,
                    date TIMESTAMP,
                    customer_id INTEGER
                )
                ''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Order_details 
                    (
                        detail_id INTEGER PRIMARY KEY,
                        order_id INTEGER,
                        good_id INTEGER,
                        quantity INTEGER
                    )
                    ''')
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
def DropDatabase():
    """
    Удадляет все таблицы из БД
    """
    conn = sql.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE Customers')
    cursor.execute('DROP TABLE Orders')
    cursor.execute('DROP TABLE Goods')
    cursor.execute('DROP TABLE Order_details')
    conn.commit()
    conn.close()
class Connection:
    """
    Класс для работы в БД
    Attributes:
        connection : подключение к БД
        cursor : установка курсора
    """
    def __init__(self):
        """
        Инициализация объекта Connection.
        """
        self.connection = sql.connect('database.db')
        self.cursor = self.connection.cursor()
    def end(self):
        """
        Сохраняет изменения и разрывает соединение с БД
        """
        self.connection.commit()
        self.connection.close()
    def to_df(self, query):
        """
        Преобразует результат выполнения sql-запроса в DataFrame

        :param query: текст sql-запроса (str)
        :return: результат запроса (DataFrame)
        """
        return pd.read_sql(query, self.connection)
    def to_list(self, query):
        """
        Преобразует результат выполнения sql-запроса в список списков (строк)

        :param query: текст sql-запроса (str)
        :return: строки запроса (list[list])
        """
        self.cursor.execute(query)
        l = self.cursor.fetchall()
        return [list(i) for i in l]
    def to_item(self, query):
        """
        Преобразует результат выполнения sql-запроса в виде вписка значений

        :param query: текст sql-запроса (str)
        :return: Первая строка запроса (list)
        """
        self.cursor.execute(query)
        item = self.cursor.fetchone()
        return item
    def clean(self):
        """
        Очистка БД от противоречивых данных (в заказе фигурирует товар или клиент, отсутствующие в БД)
        Удаляет заказы с несуществующими клиентами из Orders и информацию о них из Order_details
        Удаляет заказы с несуществующими товарами из Orders и информацию о них из Order_details
        """
        '''Удаляем заказы с несуществующими клиентами и информацию о них'''
        self.cursor.execute(f'''
                            SELECT order_id 
                            FROM Orders 
                            LEFT JOIN Customers 
                            ON Orders.customer_id = Customers.customer_id 
                            WHERE Customers.customer_id IS NULL
                            ''')
        lst = [i[0] for i in self.cursor.fetchall()]
        for order_id in lst:
            self.cursor.execute(f'''DELETE FROM Orders WHERE order_id = {order_id}''')
            self.cursor.execute(f'''DELETE FROM Order_details WHERE order_id = {order_id}''')
        '''Удаляем заказы с несуществующими товарами и информацию о них'''
        self.cursor.execute(f'''
                                SELECT detail_id
                                FROM Order_details 
                                LEFT JOIN Goods 
                                ON Order_details.good_id = Goods.good_id 
                                WHERE Goods.good_id IS NULL
                                ''')
        lst = [i[0] for i in self.cursor.fetchall()]
        for detail_id in lst:
            self.cursor.execute(f'''DELETE FROM Order_details WHERE detail_id = {detail_id}''')
            self.cursor.execute(f'''SELECT DISTINCT(Orders.order_id) FROM Orders
                                        LEFT JOIN Order_details 
                                        ON Orders.order_id = Order_details.order_id 
                                        WHERE Order_details.order_id IS NULL
                                        ''')
            lst = [i[0] for i in self.cursor.fetchall()]
            for order_id in lst:
                self.cursor.execute(f'''DELETE FROM Orders WHERE order_id = {order_id}''')
        self.end()
class Customers(Connection):
    """
    Класс для работы с таблицами БД, содержащими поле customer_id (клиент), а также связанными с ними таблицами
    """
    def __init__(self):
        """
        Инициализация объекта Customers.
        """
        super().__init__()
    def create(self, name, contact, address):
        """
        Записывает строку в Customers (customer_id, name, contact, address)
        customer_id создается функцией

        :param name: имя (название) клиента (str)
        :param contact: контакт клиента (str)
        :param address: адрес клиента (str)
        """
        self.cursor.execute(f'''INSERT INTO Customers (name, contact, address) VALUES (?, ?, ?)''',(name, contact, address))
        self.end()
    def remove(self, customer_id):
        """
        Удаление клиента из БД:
        Удаляет клиента из таблицы Customers БД
        Удаляет в все заказы клиента из таблицы Orders
        Удаляет всю информацию о заказах клиента из таблицы Order_details

        :param customer_id: уникальный номер клиента (int)
        """
        """Удаляем самого клиента"""
        self.cursor.execute(f'''DELETE FROM Customers WHERE customer_id = {customer_id}''')
        self.cursor.execute(f'''SELECT order_id FROM Orders WHERE customer_id = {customer_id}''')
        """Удаляем информацию о заказах клиента"""
        for i in [i[0] for i in self.cursor.fetchall()]:
           self.cursor.execute(f'''DELETE FROM Order_details WHERE order_id = {i}''')
        """Удаляем все заказы клиента"""
        self.cursor.execute(f'''DELETE FROM Orders WHERE customer_id = {customer_id}''')
        self.end()
    def edit(self, customer_id, name, contact, address):
        """
        Вносит изменения в атрибуты клиента в таблице Customers

        :param customer_id: уникальный номер клиента (int)
        :param name: имя (название) клиента (str)
        :param contact: контакт клиента (str)
        :param address: адрес клиента (str)
        """
        query = f'''UPDATE Customers 
                        SET 
                            name = '{name}', 
                            contact = '{contact}', 
                            address = '{address}' 
                        WHERE customer_id = {customer_id}'''
        self.cursor.execute(query)
        self.end()
    def find_query(self, name, contact, address):
        """
        Создает запрос для поиска клиента с помощью фильтра
        :param name: имя (название) клиента (str)
        :param contact: контакт клиента (str)
        :param address: адрес клиента (str)
        :return: текст запроса, который вернет всех клиентов с заданными параметрами
        """
        query =  f'''
                    SELECT * 
                    FROM Customers 
                    WHERE
                        LOWER(name) LIKE LOWER('%{name}%') AND
                        LOWER(contact) LIKE LOWER('%{contact}%') AND
                        LOWER(address) LIKE LOWER('%{address}%')
                    '''
        return query
class Orders(Connection):
    """
    Класс для работы с таблицами БД, содержащими поле order_id (заказ), а также связанными с ними таблицами
    """
    def __init__(self):
        """
        Инициализация класса
        """
        super().__init__()
    def create(self, customer_id, cart):
        """
        Создает заказ.
        Создает строку в таблице Orders
        Создает строки в таблице Order_details
        Дата заказа соответствует текущей

        :param customer_id: уникальный номер клиента (int)
        :param cart: список товаров и их количество [[good_id, good, price, quantity], ...]
        """
        start_date = dt.date(2025, 7, 1)
        end_date = dt.date(2025, 7, 31)
        random_date = start_date + dt.timedelta(days=random.randint(0, (end_date - start_date).days))
        today = dt.date.today()
        self.cursor.execute(f'''INSERT INTO Orders (customer_id, date) VALUES (?, ?)''',(customer_id, today))
        """Извлекаем id только что сформированного заказа (самый большой int)"""
        self.cursor.execute(f'''SELECT MAX(order_id) FROM Orders''')
        order_id = self.cursor.fetchone()[0]
        for i in cart:
            good_id = i[0]
            quantity = i[3]
            self.cursor.execute(f'''INSERT INTO Order_details (order_id, good_id, quantity) VALUES (?, ?, ?)''',(order_id, good_id, quantity))
        self.end()
    def remove(self, order_id):
        """
        Удаляет заказ и всю информацию о нем.
        Удаляет заказ из таблицы Orders.
        Удаляет информацию о заказе из таблицы Order_details.

        :param order_id: уникальный номер заказа (int)
        """
        self.cursor.execute(f'''DELETE FROM Orders WHERE order_id = {order_id}''')
        self.cursor.execute(f'''DELETE FROM Order_details WHERE order_id = {order_id}''')
        self.end()
    def edit(self, order_id, customer_id, cart):
        """
        Редактирует имеющийся заказ в БД
        Меняет клиента в заказе в Orders
        Удаляет информацию о заказе из Order_details и формирует новую

        :param order_id: уникальный номер заказа (Int)
        :param customer_id: уникальный номер клиента (int)
        :param cart: новый список товаров и их количество [[good_id, good, price, quantity], ...]
        """
        self.cursor.execute(f'''UPDATE Orders SET customer_id = '{customer_id}' WHERE order_id = {order_id}''')
        self.cursor.execute(f'''DELETE FROM Order_details WHERE order_id = {order_id}''')
        for i in cart:
            good_id = i[0]
            quantity = i[3]
            self.cursor.execute(f'''INSERT INTO Order_details (order_id, good_id, quantity) VALUES (?, ?, ?)''',(order_id, good_id, quantity))
        self.end()
    def find_query(self, name, good, date, address):
        """
        Создает текст запроса для поиска заказов с помощью фильтра

        :param name: уникальный номер клиента, сделавшего заказ (int)
        :param good: уникальный номер товара в заказе (int)
        :param date: дата заказа (timestamp)
        :param address: адрес клиента, сделавшего заказ (str)
        :return: текст запроса, который вернет все заказы с заданными параметрами
        """
        query =  f'''SELECT 
                        Orders.order_id AS order_id,
                        date,
                        Orders.customer_id AS customer_id
                    FROM Orders
                    JOIN Customers 
                    ON Orders.customer_id = Customers.customer_id
                    JOIN Order_details
                    ON Orders.order_id = Order_details.order_id
                    JOIN Goods
                    ON Order_details.good_id = Goods.good_id
                    WHERE 
                        LOWER(name) LIKE LOWER('%{name}%') AND
                        LOWER(good) LIKE LOWER('%{good}%') AND
                        date LIKE '%{date}%' AND
                        LOWER(address) LIKE LOWER('%{address}%')
                    GROUP BY Orders.order_id, date, Orders.customer_id, address
                    '''
        return query
class Goods(Connection):
    """
    Класс для работы с таблицами БД, содержащими поле good_id (товар), а также связанными с ними таблицами
    """
    def __init__(self):
        super().__init__()
        """
        Инициализация класса
        """
    def create(self, good, price):
        """
        Заведение нового товара в БД. Создает строку в таблице Goods.

        :param good: наименование товара (str)
        :param price: цена единицы товара (float)
        """
        self.cursor.execute(f'''INSERT INTO Goods (good, price) VALUES (?, ?)''',(good, price))
        self.end()
    def remove(self, good_id):
        """
        Удаляет товар из Goods
        Удаляет товар из всех заказов
        Удаляет все заказы, в которых только удаленный товар

        :param good_id: уникальный номер товара (int)
        """
        self.cursor.execute(f'''DELETE FROM Goods WHERE good_id = {good_id}''')
        self.cursor.execute(f'''DELETE FROM Order_details WHERE good_id = {good_id}''')
        self.cursor.execute(f'''SELECT DISTINCT(Orders.order_id) FROM Orders
                            LEFT JOIN Order_details 
                            ON Orders.order_id = Order_details.order_id 
                            WHERE Order_details.order_id IS NULL
                            ''')
        lst = [i[0] for i in self.cursor.fetchall()]
        for i in lst:
            self.cursor.execute(f'''DELETE FROM Orders WHERE order_id = {i}''')
        self.end()
    def edit(self, good_id, new_good, new_price):
        """
        Изменяет атрибуты товара в таблцие Goods

        :param good_id: уникальный номер товара (int)
        :param new_good: новое наименование товара (str)
        :param new_price: новая цента товара (float)
        """
        query = f'''UPDATE Goods SET good = '{new_good}', price = {new_price} WHERE good_id = {good_id}'''
        self.cursor.execute(query)
        self.end()
    def find_query(self, good, minprice, maxprice):
        """
        Создает текст запроса для поиска товаров с помощью фильтра

        :param good: наименование товара (str)
        :param minprice: минимальная цена (float)
        :param maxprice: максимальная цена (float)
        :return: текст запроса, возвращающего список товаров, соответствующим заданным параметрам
        """
        maximum = Connection().to_item('SELECT MAX(price) FROM Goods')[0]
        minprice = 0 if minprice == '' else minprice
        maxprice = maximum if maxprice == '' else maxprice
        query =  f'''SELECT *
                    FROM Goods
                    WHERE 
                        LOWER(good) LIKE LOWER('%{good}%') AND
                        price >= BETWEEN CAST('{minprice}' AS REAL) AND CAST('{maxprice}' AS REAL)
                    '''
        return query
