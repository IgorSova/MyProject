import sqlite3 as sql
import pandas as pd
import datetime as dt
import random
def CreateDatabase():
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
    conn = sql.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE Customers')
    cursor.execute('DROP TABLE Orders')
    cursor.execute('DROP TABLE Goods')
    cursor.execute('DROP TABLE Order_details')
    conn.commit()
    conn.close()
class Connection:
    def __init__(self):
        self.connection = sql.connect('database.db')
        self.cursor = self.connection.cursor()
    def end(self):
        self.connection.commit()
        self.connection.close()
    def to_df(self, query):
        return pd.read_sql(query, self.connection)
    def to_list(self, query):
        self.cursor.execute(query)
        l = self.cursor.fetchall()
        return [list(i) for i in l]
    def to_item(self, query):
        self.cursor.execute(query)
        item = self.cursor.fetchone()
        return item
    def clean(self):
        # Удаляем заказы с несуществующими клиентами и информацию о них
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
        # Удаляем заказы с несуществующими товарами и информацию о них
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
    def __init__(self):
        super().__init__()
    # def data(self):
    #     self.cursor.execute(f'''SELECT * FROM Customers''')
    def create(self, name, contact, address):
       self.cursor.execute(f'''INSERT INTO Customers (name, contact, address) VALUES (?, ?, ?)''',(name, contact, address))
       self.end()
    def remove(self, customer_id):
       # Удаляем самого клиента
       # Удаляем информацию о заказах клиента
       # Удаляем все заказы клиента
       self.cursor.execute(f'''DELETE FROM Customers WHERE customer_id = {customer_id}''')
       self.cursor.execute(f'''SELECT order_id FROM Orders WHERE customer_id = {customer_id}''')
       for i in [i[0] for i in self.cursor.fetchall()]:
           self.cursor.execute(f'''DELETE FROM Order_details WHERE order_id = {i}''')
       self.cursor.execute(f'''DELETE FROM Orders WHERE customer_id = {customer_id}''')
       self.end()
    def edit(self, customer_id, name, contact, address):
       query = f'''UPDATE Customers 
                        SET 
                            name = '{name}', 
                            contact = '{contact}', 
                            address = '{address}' 
                        WHERE customer_id = {customer_id}'''
       print(query)
       self.cursor.execute(query)
       self.end()
    def find_query(self, name, contact, address):
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
    def __init__(self):
        super().__init__()
    # def data(self):
    #     self.cursor.execute(f'''SELECT * FROM Orders''')
    def create(self, customer_id, cart):
        start_date = dt.date(2025, 7, 1)
        end_date = dt.date(2025, 7, 31)
        random_date = start_date + dt.timedelta(days=random.randint(0, (end_date - start_date).days))
        today = dt.date.today()
        self.cursor.execute(f'''INSERT INTO Orders (customer_id, date) VALUES (?, ?)''',(customer_id, today))
        self.cursor.execute(f'''SELECT MAX(order_id) FROM Orders''')    # Извлекаем id только что сформированного заказа (самый большой int)
        order_id = self.cursor.fetchone()[0]
        for i in cart:
            good_id = i[0]
            quantity = i[3]
            self.cursor.execute(f'''INSERT INTO Order_details (order_id, good_id, quantity) VALUES (?, ?, ?)''',(order_id, good_id, quantity))
        self.end()
    def remove(self, order_id):
        self.cursor.execute(f'''DELETE FROM Orders WHERE order_id = {order_id}''')
        self.cursor.execute(f'''DELETE FROM Order_details WHERE order_id = {order_id}''')
        self.end()
    def edit(self, order_id, customer_id, cart):
        self.cursor.execute(f'''UPDATE Orders SET customer_id = '{customer_id}' WHERE order_id = {order_id}''')
        self.cursor.execute(f'''DELETE FROM Order_details WHERE order_id = {order_id}''')
        for i in cart:
            good_id = i[0]
            quantity = i[3]
            self.cursor.execute(f'''INSERT INTO Order_details (order_id, good_id, quantity) VALUES (?, ?, ?)''',(order_id, good_id, quantity))
        self.end()
    def find_query(self, name, good, date, address):
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
    def __init__(self):
        super().__init__()
    def data(self):
        self.cursor.execute(f'''SELECT * FROM Goods''')
    def create(self, good, price):
        self.cursor.execute(f'''INSERT INTO Goods (good, price) VALUES (?, ?)''',(good, price))
        self.end()
    def remove(self, good_id):
        # Удаляем сам товар
        # Удаляем товар из всех заказов
        # Удаляем все заказы, в которых только удаленные товары
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
        query = f'''UPDATE Goods SET good = '{new_good}', price = {new_price} WHERE good_id = {good_id}'''
        self.cursor.execute(query)
        self.end()
    def find_query(self, good, minprice, maxprice):
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

