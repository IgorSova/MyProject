import db
import pandas as pd
def import_customers_csv(file):
    """
    Добавляет в БД клиентов из файла csv
    При совпадении имен заводятся разные клиенты с одинаковыми именами
    Обязательные поля:
        name (str): имя клиента
        contact (str): контакт клиента (номер телефона или email)
        address (str): адрес клиента (доставки)

    :param file: название файла из которого импортируются данные
    """
    with open(file, 'r', newline='') as f:
        df = pd.read_csv(f)
        for index, row in df.iterrows():
            db.Customers().create(name=row['name'], contact=row['contact'], address=row['address'])
        f.close()
def import_goods_csv(file):
    """
    Добавляет в БД товары из файла csv
    При совпадении наименований заводятся разные товары с одинаковыми наименованиями
    Обязательные поля:
        good (str): наименование товара
        price (float): цена единицы товара
    :param file: название файла из которого импортируются данные (str)
    """
    with open(file, 'r', newline='') as f:
        df = pd.read_csv(f)
        for index, row in df.iterrows():
            db.Goods().create(good=row['good'], price=row['price'])
        f.close()
def import_orders_csv(file):
    """
    Добавляет в БД заказы из файла csv
    При совпадении имен заводятся разные клиенты с одинаковыми именами
    Обязательные поля:
        order_id (int): номер заказа
            Нужен для группировки по заказ/клиент, чтобы разделить заказы одного клиента
            При соответствии одному заказу нескольких клиентов создаются заказы для каждого клиента
        customer_id (int): уникальный номер клиента
        good_id (int): контакт клиента (номер телефона или email)
        quantity (int): адрес клиента (доставки)
    Вспомогательные поля:
            Формируются функцией со значениями None
            Нужны, чтобы сформировать правильную структуру корзины для ее дальнейшей обработки
        good: наименование товара
        price: цена единицы товара

    :param file: название файла из которого импортируются данные
    """
    with open(file, 'r', newline='') as f:
        df = pd.read_csv(f)
        df['good'] = None
        df['price'] = None
        df = df.groupby(['order_id', 'customer_id']).apply(lambda x: pd.Series({'cart': (x[['good_id', 'good', 'price', 'quantity']].values)})).reset_index()
        for index, row in df.iterrows():
            db.Orders().create(customer_id=row['customer_id'], cart=row['cart'])
        db.Connection().clean()
        f.close()
def import_customers_json(file):
    """
    Добавляет в БД клиентов из файла json
    При совпадении имен заводятся разные клиенты с одинаковыми именами
    Обязательные поля:
        name (str): имя клиента
        contact (str): контакт клиента (номер телефона или email)
        address (str): адрес клиента (доставки)

    :param file: название файла из которого импортируются данные
    """
    with open(file, 'r', newline='') as f:
        content = f.read()
        df = pd.read_json(content)
        for index, row in df.iterrows():
            db.Customers().create(name=row['name'], contact=row['contact'], address=row['address'])
        f.close()
def import_goods_json(file):
    """
    Добавляет в БД товары из файла json
    При совпадении наименований заводятся разные товары с одинаковыми наименованиями
    Обязательные поля:
        good (str): наименование товара
        price (float): цена единицы товара
    :param file: название файла из которого импортируются данные (str)
    """
    with open(file, 'r', newline='') as f:
        content = f.read()
        df = pd.read_json(content)
        for index, row in df.iterrows():
            db.Goods().create(good=row['good'], price=row['price'])
        f.close()
def import_orders_json(file):
    """
    Добавляет в БД заказы из файла json
    При совпадении имен заводятся разные клиенты с одинаковыми именами
    Обязательные поля:
        order_id (int): номер заказа
            Нужен для группировки по заказ/клиент, чтобы разделить заказы одного клиента
            При соответствии одному заказу нескольких клиентов создаются заказы для каждого клиента
        customer_id (int): уникальный номер клиента
        good_id (int): контакт клиента (номер телефона или email)
        quantity (int): адрес клиента (доставки)
    Вспомогательные поля:
            Формируются функцией со значениями None
            Нужны, чтобы сформировать правильную структуру корзины для ее дальнейшей обработки
        good: наименование товара
        price: цена единицы товара

    :param file: название файла из которого импортируются данные
    """
    with open(file, 'r', newline='') as f:
        content = f.read()
        df = pd.read_json(content)
        df = df.groupby(['order_id', 'customer_id']).apply(lambda x: pd.Series({'cart': (x[['good_id', 'good', 'price', 'quantity']].values)})).reset_index()
        for index, row in df.iterrows():
            db.Orders().create(customer_id=row['customer_id'], cart=row['cart'])
        db.Connection().clean()
        f.close()
def export_csv(query, filename):
    """
    Формирует файл csv на основе написанного пользователем запроса
    :param query: текст запроса
    :param filename: название файла с указанием типа файла '.csv' и (опционально) адреса
    """
    data = db.Connection().to_df(query)
    data.to_csv(path_or_buf=filename, index=False)
def export_json(query, filename):
    """
    Формирует файл json на основе написанного пользователем запроса
    :param query: текст запроса
    :param filename: название файла с указанием типа файла '.json' и (опционально) адреса
    """
    data = db.Connection().to_df(query)
    data.to_json(path_or_buf= filename, index=True)
