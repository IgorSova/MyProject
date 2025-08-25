import db
import pandas as pd
def import_customers_csv(file):
    with open(file, 'r', newline='') as f:
        df = pd.read_csv(f)
        for index, row in df.iterrows():
            db.Customers().create(name=row['name'], contact=row['contact'], address=row['address'])
        f.close()
def import_goods_csv(file):
    with open(file, 'r', newline='') as f:
        df = pd.read_csv(f)
        for index, row in df.iterrows():
            db.Goods().create(good=row['good'], price=row['price'])
        f.close()
def import_orders_csv(file):
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
    with open(file, 'r', newline='') as f:
        content = f.read()
        df = pd.read_json(content)
        for index, row in df.iterrows():
            db.Customers().create(name=row['name'], contact=row['contact'], address=row['address'])
        f.close()
def import_goods_json(file):
    with open(file, 'r', newline='') as f:
        content = f.read()
        df = pd.read_json(content)
        for index, row in df.iterrows():
            db.Goods().create(good=row['good'], price=row['price'])
        f.close()
def import_orders_json(file):
    with open(file, 'r', newline='') as f:
        content = f.read()
        df = pd.read_json(content)
        df = df.groupby(['order_id', 'customer_id']).apply(lambda x: pd.Series({'cart': (x[['good_id', 'good', 'price', 'quantity']].values)})).reset_index()
        for index, row in df.iterrows():
            db.Orders().create(customer_id=row['customer_id'], cart=row['cart'])
        db.Connection().clean()
        f.close()
def export_csv(query):
    data = db.Connection().to_df(query)
    data.to_csv(path_or_buf='report.csv', index=False)
def export_json(query):
    data = db.Connection().to_df(query)
    data.to_json(path_or_buf='report.json', index=True)