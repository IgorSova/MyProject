"""
Модуль, содержащий основные классы: Orders, Customers, Goods.
Orders - заказы
Customers - покупатели
Goods - товары
"""
import db as db
class Orders:
    """
    Класс для обработки заказов

    Attributes:
        order_id (int): уникальный номер заказа
        customer_id (int): уникальный номер клиента, сделавшего заказ. Одному заказу соответствует только один id клиента
    """
    def __init__(self, order_id, customer_id):
        """
        Инициализация объекта Orders.
        """
        self.order_id = order_id
        self.customer_id = customer_id
    def create(self, cart):
        """
        Создает заказ в БД. Вносит данные о заказе в таблицы Orders и Order_details.

        :param cart: список товаров в корзине [[good_id, good, price, quantity], ...]:
                good_id (int) - уникальный номер товара
                good (str) - название товара
                price (float) - цена товара
                quantity (int) - количество единиц товара в заказе
        :return: Возвращает объект Orders()
        """
        db.Orders().create(customer_id=self.customer_id, cart=cart)
        return self
    def remove(self):
        """
        Удаляет данные о заказе из таблиц Orders и Order_details
        :return: Возвращает объект
        """
        db.Orders().remove(order_id=self.order_id)
        return self
    def edit(self, customer_id, cart):
        """
        Редактирует заказ в БДЖ
        Меняет в БД номер клиента, сделавшего заказ
        Удаляет из таблицы Order_details информацию о заказе и формирует новую

        :param customer_id: уникальный номер нового клиента, сделавшего заказ (int)
        :param cart: новый список товаров и их количество [[good_id, good, price, quantity], ...]
            good_id (int) - уникальный номер товара
            good (str) - название товара
            price (float) - цена товара
            quantity (int) - количество единиц товара в заказе
        :return: Возвращает объект
        """
        db.Orders().edit(order_id=self.order_id, customer_id=customer_id, cart=cart)
        return self
    def find_customers(self):
        """
            Функция поиска клиента, сделавшего заказ

            Args:
                customer_id (int): уникальный номер клиента, сделавшего заказ
                order_id (int): уникальный номер заказа
                cart (list[list]) - новая корзина товаров
            Returns:
                Возвращает из БД строку клиента либо создает пустой объект класса Customers в случае ошибки
        """
        try:
            query = db.Connection().to_df(f'SELECT * FROM Customers WHERE customer_id = {self.customer_id}').iloc[0]
            customer = Customers(customer_id=self.customer_id, name=query['name'], contact=query['contact'],address=query['address'])
        except:
            customer = Customers(customer_id=None, name=None, contact=None, address=None)
        return customer
class Customers:
    """
    Класс для обработки клиентов

    Attributes:
        customer_id (int): уникальный номер клиента
        name (str): имя клиента
        contact (str): контакт клиента (номер телефона или email)
        address (str): адрес клиента (доставки)
    """
    def __init__(self, customer_id, name, contact, address):
        """
        Инициализация объекта Customers
        """
        self.customer_id = customer_id
        self.name = name
        self.contact = contact
        self.address = address
    def create(self):
        """
        Создание нового клиента в БД. Вносит нового клиента в таблицу Customers.
        :return: Возвращает создаваемый объект
        """
        db.Customers().create(name=self.name, contact=self.contact, address=self.address)
        return self
    def remove(self):
        """
        Удаляет клиента из БД:
        Удаляет строку клиента из БД из таблицы Customers
        Удаляет все заказы клиента из таблицы Orders
        Удаляет информацию о заказах клиента из таблицы Order_details

        :return: Возвращает удаляемый объект
        """
        db.Customers().remove(customer_id=self.customer_id)
        return self
    def edit(self, new_name, new_contact, new_address):
        """
        Редактирует атрибуты клиента в БД

        :param new_name: новое имя (название) клиента (str)
        :param new_contact: новый контакт клиента (номер телефона или email) (str)
        :param new_address: новый адрес клиента (str)
        :return: Возвращает объект с новыми атрибутами
        """
        db.Customers().edit(customer_id=self.customer_id, name=new_name, contact=new_contact, address=new_address)
        return self
class Goods:
    """
    Класс для работы с товарами

    Attributes:
        good_id (int): уникальный номер товара
        good (str): наименование товара
        price (float): цена единицы товара
    """
    def __init__(self, good_id, good, price):
        """
        Инициализация объекта
        """
        self.good_id = good_id
        self.good = good
        self.price = price
    def create(self):
        """
        Создание товара в БД. Вносит новый товар в таблицу Goods.

        :return: Возвращает создаваемый объект
        """
        db.Goods().create(good=self.good, price=self.price)
        return self
    def remove(self):
        """
        Удаляет строку товара из БД из таблицы Goods
        Удаляет все заказы, содержащие только удаляемый товар, из таблицы Orders
        Удаляет информацию от товаре в заказах из таблицы Order_details

        :return: Возвращает удаляемый объект
        """
        db.Goods().remove(good_id=self.good_id)
        return self
    def edit(self, new_good, new_price):
        """
        Редактирует атрибуты товара (good, price)
        :param new_good:  новое имя (название) клиента (str)
        :param new_price: новая цена товара (float)
        :return: Возвращает объект с новыми атрибутами
        """
        db.Goods().edit(good_id=self.good_id, new_good=new_good, new_price=new_price)
        return self
