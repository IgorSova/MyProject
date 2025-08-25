import db as db
class Orders:
    def __init__(self, order_id, customer_id):
        self.order_id = order_id
        self.customer_id = customer_id
    def create(self, cart):
        db.Orders().create(customer_id=self.customer_id, cart=cart)
        return self
    def remove(self):
        db.Orders().remove(order_id=self.order_id)
        return self
    def edit(self, customer_id, cart):
        db.Orders().edit(order_id=self.order_id, customer_id=customer_id, cart=cart)
        return self
    def find_customers(self):
        try:
            query = db.Connection().to_df(f'SELECT * FROM Customers WHERE customer_id = {self.customer_id}').iloc[0]
            customer = Customers(customer_id=self.customer_id, name=query['name'], contact=query['contact'],address=query['address'])
        except:
            customer = Customers(customer_id=None, name=None, contact=None, address=None)
        return customer
class Customers:
    def __init__(self, customer_id, name, contact, address):
        self.customer_id = customer_id
        self.name = name
        self.contact = contact
        self.address = address
    def create(self):
        db.Customers().create(name=self.name, contact=self.contact, address=self.address)
        return self
    def remove(self):
        db.Customers().remove(customer_id=self.customer_id)
        return self
    def edit(self, new_name, new_contact, new_address):
        db.Customers().edit(customer_id=self.customer_id, name=new_name, contact=new_contact, address=new_address)
        return self
class Goods:
    def __init__(self, good_id, good, price):
        self.good_id = good_id
        self.good = good
        self.price = price
    def create(self):
        db.Goods().create(good=self.good, price=self.price)
        return self
    def remove(self):
        db.Goods().remove(good_id=self.good_id)
        return self
    def edit(self, new_good, new_price):
        db.Goods().edit(good_id=self.good_id, new_good=new_good, new_price=new_price)
        return self
class Order_details:
    def __init__(self, detail_id, order_id, good_id, quantity):
        self.detail_id = detail_id
        self.order_id = order_id
        self.good_id = good_id
        self.quantity = quantity
    def create(self):
        db.Order_details.create()
    def remove(self):
        db.Order_details.remove()
    def edit(self):
        db.Order_details.edit()

