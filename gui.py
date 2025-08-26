import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import re
import db as db
import models
import analysis
import admin
class Window(tk.Tk):
    def __init__(self):
        """
        Класс для построения окон приложения

        Attributes:
            title - номер строки по умолчанию
            geometry - номер столбца по умолчанию
            attributes - текст запроса, возвращающего все данные из таблицы Orders (для tree)
            bind - бинд окна
            style - стиль заголовков tree
            row - номер строки по умолчанию
            column - номер столбца по умолчанию
            query - текст запроса, возвращающего все данные из таблицы Orders (для tree)
        """
        super().__init__()
        self.title('Shop manager')
        self.geometry('1050x800')
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', self.exit_fullscreen)
        self.style = ttk.Style()
        self.style.configure('Treeview.Heading',
                             foreground="red",  # Цвет текста заголовков
                             background="red",  # Цвет фона заголовков. Не работает, даже в хрестоматийных примерах.
                             font='italic'  # Тип шрифта. Люброй формат просто увеличивает текст, больше ничего.
                             )
        self.main_widgets()
        # Управляющие переменные
        self.frame_width = tk.IntVar(value=1000)
        self.row = tk.IntVar()
        self.column = tk.IntVar(value=0)
        self.query = tk.StringVar(value='')
        '''Представление по умолчанию'''
        Orders.show(self)
    def activate_entry(self, entry):
        """
        Стирает значение из entry и меняет конфигурацию строки ввода, в том числе снимает бинд
        :param entry: строка ввода, к которой применяется функция
        """
        entry.config(foreground='black')
        entry.delete(0, tk.END)
        entry.bind('<ButtonRelease-1>', lambda x: None)
    def valid_contact(self, contact):
        """
        Проверка корректного ввода контакта клиента (contact)
            phone - начинается с +7, содержит ровно 10 других цифр
            email - название почты содержит только буквы или символы '+-_',
                    потом собака @,
                    потом домен - буквы или символы '.-', потом не менее 2 букв

        :param contact: контакт клиента (номер телефона или email) (str)
        :return: соответствие контакта шаблону (bool)
        """
        phone = re.search(r'^\+7\d{10}$', contact) is not None
        email = re.search(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', contact) is not None
        if phone or email:
            return True
        else:
            tk.messagebox.showerror(message='Contact is not valid\nEnter e-mail or phone number in +7 format')
            return False
    def valid_name(self, name):
        """
        Проверка корректного ввода имени клиента
            name - буквы или символы '- '

        :param name: имя клиента (str)
        :return: соответствие имени шаблону (bool)
        """
        value = re.search(r'^[A-Za-zА-Яа-яЁё -]+$', name) is not None
        if value:
            return True
        else:
            tk.messagebox.showerror(message='Customer name is not valid')
            return False
    def valid_good(self, good):
        """
        Проверка корректного ввода наименования товара
            good - буквы или символы '- '

        :param good: наименование товара (str)
        :return: соответствие наименования шаблону (bool)
        """
        value = re.search(r'^[A-Za-zА-Яа-яЁё -]+$', good) is not None
        if value:
            return True
        else:
            tk.messagebox.showerror(message='Good name is not valid')
            return False
    def valid_address(self, address):
        """
        Проверка корректного ввода адреса клиента
            address - буквы или символы ' -.,'

        :param address: адрес клиента (str)
        :return: соответствие адреса клиента шаблону (bool)
        """
        value = re.search(r'^[A-Za-zА-Яа-яЁё0-9- \\.\\,]+$', address) is not None
        if value:
            return True
        else:
            tk.messagebox.showerror(message='Address is not valid')
            return False
    def valid_quantity(self, quantity):
        """
        Проверка корректности введенного количества товара
        :param quantity: количество товара
        :return: соответствие количества товара допустимомым значениям
        """
        try:
            a = int(quantity) > 0
        except:
            return False
        else:
            return a
    def valid_price(self, price):
        """
        Проверка корректности введенной цены товара
        :param price:
        :return: соответствие цены товара допустимомым значениям
        """
        try:
            a = float(price)
        except:
            tk.messagebox.showerror(message='Price must be positive float')
            return False
        else:
            if a <= 0:
                tk.messagebox.showerror(message='Price must be positive float')
                return False
            else:
                return True
    def deactivate(self, widgets: list[str]):
        """
        Делает указанные кнопки неактивными

        :param widgets: список имен (атрибут name) кнопок, которые нужно сделать неактивными
        """
        for i in self.winfo_children():
            name = self.nametowidget(i).winfo_name()
            exam = name in widgets
            typeexam = isinstance(i, tk.Button)
            if exam and typeexam:
                i.config(relief=SUNKEN, state=DISABLED)
    def activate(self, widgets: list[str]):
        """
        Делает указанные кнопки активными

        :param widgets: список имен (атрибут name) кнопок, которые нужно сделать активными
        """
        for i in self.winfo_children():
            name = self.nametowidget(i).winfo_name()
            exam = name in widgets
            typeexam = isinstance(i, tk.Button)
            if exam and typeexam:
                i.config(relief=RAISED, state=ACTIVE)
    def tree(self):
        """
        Возвращает текущее tree

        :return: текущее tree
        """
        return self.tree
    def exit_fullscreen(self, event):
        """
        Выходит из полноэкранного режима

        :param event: событие в bind
        """
        self.attributes('-fullscreen', False)
    def treeview(self, query):
        """
        Формирует tree в текущем окне

        :param query: запрос, на основе которого формируется tree
        """
        df = db.Connection().to_df(query)
        columns = list(df)
        items = list(df.itertuples(index=False, name=None))
        length = len(columns)
        self.tree = ttk.Treeview(master=self, columns=columns, show='headings', selectmode=EXTENDED, name='tree')
        self.tree.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky='n')
        for i in columns:
            self.tree.heading(i, text=i, anchor=W)
            self.tree.column(i, width=int(1000/length), stretch=True)
        for i in items:
            self.tree.insert('', END, values=i)
    def sortcolumn(self, col, reverse):
        """
        Настраивает сортировку для столбцов tree
        Вызывается в дальнейшем по клику на заголовок tree

        :param col: название столбца tree (str)
        :param reverse: маркер обратной сортировки (desc)
        """
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse)
        for index, (_, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sortcolumn(col, not reverse))
    def main_widgets(self):
        """
        Основные виджеты рабочего окна (присутствуют во всех представлениях окна):
            Кнопка "Orders"
            Кнопка "Customers"
            Кнопка "Goods"
            Кнопка "Analysis"
            Кнопка "Admin"
        """
        # Кнопка "Заказы"
        self.orders_button = tk.Button(self, name='orders',
                                            text='Orders',
                                            height=3,
                                            width=25,
                                            background='white',
                                            command=lambda: Orders.show(self)
                                            )
        self.orders_button.grid(row=0, column=0, padx=0, pady=10, sticky='n')
        # Кнопка "Клиенты"
        self.customers_button = tk.Button(self, name='customers',
                                               text='Customers',
                                               height=3,
                                               width=25,
                                               background='white',
                                               command=lambda: Customers.show(self)
                                               )
        self.customers_button.grid(row=0, column=1, padx=0, pady=10, sticky='n')
        # Кнопка "Товары"
        self.goods_button = tk.Button(self, name='goods',
                                           text='Goods',
                                           height=3,
                                           width=25,
                                           background='white',
                                           command=lambda: Goods.show(self)
                                           )
        self.goods_button.grid(row=0, column=2, padx=0, pady=10, sticky='n')
        self.analisys_button = tk.Button(self, name='analysis',
                                           text='Analysis',
                                           height=3,
                                           width=25,
                                           background='white',
                                           command=lambda: Analysis.show(self)
                                           )
        self.analisys_button.grid(row=0, column=3, padx=0, pady=10, sticky='n')
        self.admin_button = tk.Button(self, name='admin',
                                              text='Admin',
                                              height=3,
                                              width=25,
                                              background='white',
                                              command=lambda: Admin().main_widgets()
                                              )
        self.admin_button.grid(row=0, column=4, padx=0, pady=10, sticky='n')
    def clean_frame(self):
        """
        Удаляет все виджеты из окна
        """
        for i in self.winfo_children():
            i.destroy()
    def destroy_widgets(self, condition, wtype):
        """
        Удаляет все виджеты, название которых соответствует шаблону и тип соответствует заданному

        :param condition: в имени виджета (атрибут name) содержится строка condition
        :param wtype: тип виджета
        """
        for i in self.winfo_children():
            i.destroy() if ((condition in str(i)) and (isinstance(i, wtype))) else False
class Orders():
    def __init__(self):
        """
        Класс для построения виджетов для работы с клиентами

        Attributes:
            row - номер строки по умолчанию
            column - номер столбца по умолчанию
            query - текст запроса, возвращающего все данные из таблицы Orders (для tree)
        """
        self.row = tk.IntVar(value=3)
        self.condition = tk.IntVar(value=0)
        self.query = tk.StringVar(value='SELECT * FROM Orders')
    def show(self):
        """
        Удалает все виджеты
        Создает основные виджеты окна (main_widgets)
        Создает специфические для представления заказов виджеты:
            Window.tree на основе таблицы БД Orders
            create_button - кнопка для перехода в представление создания заказа
            edit_button - кнопка для перехода в представление редактирования заказа
            remove_button - кнопка удаления заказа (удаляется в текущем представлении)
            Виджеты для поиска заказа (find)
        """
        Window.clean_frame(self)
        Window.main_widgets(self)
        Window.treeview(self, query=Orders().query.get())
        Orders.sort_tree(self)
        self.create_button = tk.Button(master=self, name='create', text='New order', width=15, command=lambda: Orders.create_frame(self))
        self.create_button.grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.edit_button = tk.Button(master=self, name='edit', text='Edit order', width=15, command=lambda: Orders.edit_frame(self))
        self.edit_button.grid(row=2, column=1, sticky='w', padx=10, pady=10)
        self.remove_button = tk.Button(master=self, name='remove', text='Delete order', width=15, command=lambda: Orders.remove(self))
        self.remove_button.grid(row=2, column=2, sticky='w', padx=10, pady=10)

        self.find_label = tk.Label(name='find_label', text='Filter orders', font='bold')
        self.find_label.grid(row=2, column=3, padx=10, pady=10, sticky='w')

        self.find_name_label = tk.Label(name='find_name_label', text='customer')
        self.find_name_label.grid(row=3, column=3, padx=10, pady=0, sticky='w')
        self.find_name_entry = tk.Entry(name='find_name_entry')
        self.find_name_entry.grid(row=3, column=4, padx=10, pady=0, sticky='w')

        self.find_good_label = tk.Label(name='find_good_label', text='good')
        self.find_good_label.grid(row=4, column=3, padx=10, pady=0, sticky='w')
        self.find_good_entry = tk.Entry(name='find_good_entry')
        self.find_good_entry.grid(row=4, column=4, padx=10, pady=0, sticky='w')

        self.find_date_label = tk.Label(name='find_date_label', text='date')
        self.find_date_label.grid(row=5, column=3, padx=10, pady=0, sticky='w')
        self.find_date_entry = tk.Entry(name='find_date_entry', foreground='grey')
        self.find_date_entry.grid(row=5, column=4, padx=10, pady=0, sticky='w')
        self.find_date_entry.insert(0, '2025-08-15')
        self.find_date_entry.bind('<ButtonRelease-1>', lambda x: Window.activate_entry(self, self.find_date_entry))

        self.find_address_label = tk.Label(name='find_address_label', text='address')
        self.find_address_label.grid(row=6, column=3, padx=10, pady=0, sticky='w')
        self.find_address_entry = tk.Entry(name='find_address_entry')
        self.find_address_entry.grid(row=6, column=4, padx=10, pady=0, sticky='w')

        self.find_button = tk.Button(name='find_button', text='Find', width=15, command=lambda: Orders.find(self,
                                                                                        name=self.find_name_entry.get(),
                                                                                        good=self.find_good_entry.get(),
                                                                                        date=self.find_date_entry.get(),
                                                                                        address=self.find_address_entry.get()
                                                                                        ))
        self.find_button.grid(row=7, column=3, padx=10, pady=10, sticky='w')

        Window.deactivate(self, ['orders'])
    def sort_tree(self):
        """
        Назначает столбцам tree сортировку по клику на заголовки
        """
        Window.tree(self).heading(column='order_id', command= lambda: Window.sortcolumn(self, col='order_id', reverse=False))
        Window.tree(self).heading(column='date', command= lambda: Window.sortcolumn(self, col='date', reverse=False))
        Window.tree(self).heading(column='customer_id', command= lambda: Window.sortcolumn(self, col='customer_id', reverse=False))
    def add_good_to_cart(self, selection):
        """
        Добавляет выбранный товар в корзину при создании или изменении заказа а также показывает его в представлении

        :param selection: [good_id, good, price, quantity] - quantity отсутствует при создании заказа
        """
        item = selection
        item[0] = int(selection[0])
        item[2] = float(selection[2])
        try:
            quantity = item.pop(3)
        except:
            quantity = ''
        if item not in self.cart:
            r = 5 + self.cartlen
            self.cart.append(item)
            good_id = item[0]
            good = item[1]

            button_name = f'{good_id} button'
            tk.Label(name=f'{good_id} label', text=f'{good}').grid(row=r, column=1, padx=10, pady=0, sticky='w')
            entry = tk.Entry(name=f'{good_id} quantity')
            entry.grid(row=r, column=2, padx=10, pady=0, sticky='w')
            entry.insert(0, quantity)
            tk.Button(name=button_name, text=f'Delete', width=10, command=lambda: remove_good(button_name)).grid(row=r, column=3, padx=10, pady=0, sticky='w')
            self.confirm_button.grid(row=r + 1)
            self.cartlen += 1
        def remove_good(button_name):
            """
            Удаляет товар из корзины
            :param button_name: имя кнопки (str)
            """
            good_id = int(button_name.split(' ', 1)[0])
            label = self.nametowidget(f'{good_id} label')
            entry = self.nametowidget(f'{good_id} quantity')
            button = self.nametowidget(button_name)
            self.cartlen -= 1
            label.destroy()
            entry.destroy()
            button.destroy()
            for i, v in enumerate(self.cart):
                if v[0] == good_id:
                    self.cart.pop(i)
                    print(self.cart)
            r = 5
            for i in self.winfo_children():
                name = str(i)
                if re.match(r'^\.\d', name):
                    typ = type(i)
                    ind = [tk.Label, tk.Entry, tk.Button].index(typ)
                    i.grid(row=r, column=ind + 1)
                    r += 1 if ind == 2 else 0
            self.confirm_button.grid(row= r)
    def create_frame(self):
        """
        Удаляет виджеты поиска из окна
        Создает представление создания заказа:
             customer_select_button - кнопка перехода к выбору клиента
             good_select_button - кнопка перехода к выбору товаров
             exit_button - кнопка возврата в представление Orders
             confirm_button - кнопка подтверждения изменений
        """
        for i in Window.winfo_children(self):
            i.destroy() if 'find' in str(i) else False
        self.cart = []
        self.cartlen = len(self.cart)
        self.row.set(value=5)
        self.customer_id = None

        self.customer_select_button = tk.Button(master=self, name='select customer', text='Select customer', width=15, command=lambda: Orders.select_customer(self))
        self.customer_select_button.grid(row=3, column=0, sticky='w', padx=10, pady=10)
        self.good_select_button = tk.Button(master=self, name='select good', text='Select goods', width=15,command=lambda: Orders.select_goods(self))
        self.good_select_button.grid(row=3, column=1, sticky='w', padx=10, pady=10)
        self.exit_button = tk.Button(master=self, name='exit', text='Exit', width=15, command=lambda: Orders.show(self))
        self.exit_button.grid(row=3, column=2, sticky='w', padx=10, pady=10)
        Window.deactivate(self, ['orders', 'customers', 'goods', 'analysis', 'admin', 'create', 'edit', 'remove'])
        # Настраиваем заголовкм
        tk.Label(text='Customer', font='bold', name='customer title').grid(row=4, column=0, padx=10, pady=0, sticky='w')
        tk.Label(text='Good', font='bold', name='good title').grid(row=4, column=1, padx=10, pady=0, sticky='w')
        tk.Label(text='Quantity', font='bold', name='quantity title').grid(row=4, column=2, padx=10, pady=0, sticky='w')
        self.confirm_button = tk.Button(master=self, name='confirm', text='Confirm', width=15, command=lambda: Orders.create(self))
        self.confirm_button.grid(row=5 + self.cartlen, column=2, sticky='w', padx=10, pady=0)
    def select_customer(self):
        """
        Переход в представление выбора клиента:
        Удаляется текущее tree и формируется tree Customers
        Показываеются данные клиента, которому создается заказ
        """
        def show_customer():
            """
            Устанавливает клиента в заказ и показывает его в окне
            """
            selection = Window.tree(self).selection()
            for i in selection:
                item = list(self.tree.item(i, 'values'))
                self.customer_id = item[0]
                self.name = item[1]
                self.contact = item[2]
                self.address = item[3]
                tk.Label(text=f'customer_id: {self.customer_id}', name='customer customer_id').grid(row=5, column=0, padx=10, pady=0, sticky='nw')
                tk.Label(text=f'name: {self.name}', name='customer name', wraplength=100).grid(row=6, column=0, padx=10, pady=0, sticky='w')
                tk.Label(text=f'contact: {self.contact}', name='customer contact', wraplength=100).grid(row=7, column=0, padx=10, pady=0, sticky='nw')
                tk.Label(text=f'address: {self.address}', name='customer address', wraplength=100).grid(row=8, column=0, padx=10, pady=0, sticky='nw', rowspan=3)
        Window.tree(self).destroy()
        Window.treeview(self, query=Customers().query.get())
        Customers.sort_tree(self)
        Window.tree(self).configure(selectmode=BROWSE)
        Window.tree(self).bind('<Double Button-1>', lambda x: show_customer())
    def select_goods(self):
        """
        Переход в представление выбора товара:
        Удаляется текущее tree и формируется tree Goods
        """
        Window.tree(self).destroy()
        Window.treeview(self, query=Goods().query.get())
        Goods.sort_tree(self)
        Window.tree(self).configure(selectmode=BROWSE)
        Window.tree(self).bind('<Double Button-1>', lambda x: Orders.add_good_to_cart(self, list(self.tree.item(Window.tree(self).selection()[0], 'values'))))
    def create(self):
        """
        Проверяет корректность введенных данных формирует заказ
        """
        if self.customer_id is None:
            return tk.messagebox.showerror(message='Select customer')
        if self.cart == []:
            return tk.messagebox.showerror(message='Select goods')
        quantities = []
        for i in self.winfo_children():
            if (isinstance(i, tk.Entry)) and ('quantity' in str(i)):
                quantity = i.get()
                if Window.valid_quantity(self, quantity=quantity):
                    quantities.append(quantity)
        try:
            for i, val in enumerate(self.cart):
                self.cart[i].append(quantities[i])
        except:
            return tk.messagebox.showerror(message=f'Quantity must be integer. Enter correct quantities')
        action = tk.messagebox.askyesno(message=f'Create order for "{self.name}" to "{self.address}"?')
        if action:
            models.Orders(order_id=None, customer_id=self.customer_id).create(cart=self.cart)
            tk.messagebox.showinfo(message=f'Order created')
            Orders.show(self)
    def remove(self):
        """
        Удаляет заказ из БД
        """
        selection = Window.tree(self).selection()
        if selection == ():
            tk.messagebox.showwarning(message=f'Select orders to delete')
        else:
            action = tk.messagebox.askyesno(message=f'Delete order?')
            if action:
                selection = Window.tree(self).selection()
                for i in selection:
                    order_id = list(self.tree.item(i, 'values'))[0]
                    models.Orders(order_id=order_id, customer_id=None).remove()
                Orders.show(self)
    def edit_frame(self):
        """
        Удаляет виджеты поиска из окна
        Создает представление редактирования заказа:
            Информация о клиенте
            Корзина заказа
            customer_select_button - кнопка перехода к выбору клиента
            good_select_button - кнопка перехода к выбору товаров
            exit_button - кнопка возврата в представление Orders
            confirm_button - кнопка подтверждения изменений
        """
        selection = Window.tree(self).selection()
        if len(selection) != 1:
            tk.messagebox.showwarning(message='Choose single order')
            Orders.show(self)
        else:
            for i in Window.winfo_children(self):
                i.destroy() if 'find' in str(i) else False
            item = list(self.tree.item(selection, 'values'))
            self.order_id = item[0]
            self.customer_id = item[2]
            self.customer = models.Orders(order_id=self.order_id, customer_id=self.customer_id).find_customers()
            self.name = self.customer.name
            self.contact = self.customer.contact
            self.address = self.customer.address

            Window.deactivate(self, ['orders', 'customers', 'goods', 'analysis', 'admin', 'create', 'edit', 'remove'])

            # Настраиваем заголовкм
            tk.Label(text='Customer', font='bold', name='customer title').grid(row=4, column=0, padx=10, pady=0, sticky='nw')
            tk.Label(text='Good', font='bold', name='good title').grid(row=4, column=1, padx=10, pady=0, sticky='nw')
            tk.Label(text='Quantity', font='bold', name='quantity title').grid(row=4, column=2, padx=10, pady=0, sticky='nw')

            self.customer_id_label = tk.Label(text=f'customer_id: {self.customer_id}', name='customer customer_id')
            self.customer_id_label.grid(row=5, column=0,padx=10, pady=0,sticky='nw')
            self.name_label = tk.Label(text=f'name: {self.name}', name='customer name')
            self.name_label.grid(row=6, column=0, padx=10,pady=0, sticky='nw')
            self.contact_label = tk.Label(text=f'contact: {self.contact}', name='customer contact')
            self.contact_label.grid(row=7, column=0, padx=10,pady=0, sticky='nw')
            self.address_label = tk.Label(text=f'address: {self.address}', name='customer address', wraplength=100)
            self.address_label.grid(row=8, column=0, padx=10, pady=0, sticky='nw')

            self.customer_select_button = tk.Button(name='select customer', text='Select customer', width=15, command=lambda: show_customers())
            self.customer_select_button.grid(row=3, column=0, padx=10, pady=0, sticky='w')
            self.good_select_button = tk.Button(name='add good', text='Add good', width=15, command=lambda: show_goods())
            self.good_select_button.grid(row=3, column=1, padx=10, pady=0, sticky='w')
            self.exit_button = tk.Button(master=self, name='exit', text='Exit', width=15, command=lambda: Orders.show(self))
            self.exit_button.grid(row=3, column=2, sticky='w', padx=10, pady=10)

            self.cart = db.Connection().to_list(f'''
                                                    SELECT 
                                                        Order_details.good_id AS good_id, 
                                                        good, 
                                                        Goods.price AS price,
                                                        Order_details.quantity AS quantity 
                                                    FROM Order_details 
                                                    JOIN Goods ON Order_details.good_id = Goods.good_id 
                                                    WHERE order_id = {self.order_id}
                                                ''')
            self.cartlen = len(self.cart)

            self.confirm_button = tk.Button(master=self, name='confirm', text='Confirm', width=15, command=lambda: Orders.edit(self))
            self.confirm_button.grid(row=5 + self.cartlen, column=2, sticky='w', padx=10, pady=0)

            items = [i for i in self.cart]
            self.cart = []
            self.cartlen = 0
            for i in items:
                Orders.add_good_to_cart(self, i)
        def show_customers():
            """
            Переход в представление выбора клиента:
            Удаляется текущее tree и формируется tree Customers
            Показываеются данные клиента, которому создается заказ
            """
            Window.tree(self).destroy()
            Window.treeview(self, query=Customers().query.get())
            Customers.sort_tree(self)
            Window.tree(self).configure(selectmode=BROWSE)
            Window.tree(self).bind('<Double Button-1>', lambda x: select_customer())
            def select_customer():
                """
                Устанавливает клиента в заказ и показывает его в окне
                """
                selection = Window.tree(self).selection()
                for i in selection:
                    item = list(self.tree.item(i, 'values'))
                    self.customer_id = item[0]
                    self.name = item[1]
                    self.contact = item[2]
                    self.address = item[3]

                    self.customer_id_label.config(text=f'customer_id:    {self.customer_id}')
                    self.name_label.config(text=f'name:                {self.name}')
                    self.contact_label.config(text=f'contact:             {self.contact}')
                    self.address_label.config(text=f'address:             {self.address}')

                    Window.treeview(self, query=Orders().query.get())
        def show_goods():
            """
            Переход в представление выбора товаров:
            Удаляется текущее tree и формируется tree Goods
            """
            Window.tree(self).destroy()
            Window.treeview(self, query=Goods().query.get())
            Goods.sort_tree(self)
            Window.tree(self).configure(selectmode=BROWSE)
            Window.tree(self).bind('<Double Button-1>', lambda x: Orders.add_good_to_cart(self, list(self.tree.item(Window.tree(self).selection()[0], 'values'))))
    def edit(self):
        """
        Проверяет корректность введенных данных сохраняет изменения в заказе
        """
        if self.cart == []:
            return tk.messagebox.showerror(message='Select goods')
        quantities = []
        for i in self.winfo_children():
            if (isinstance(i, tk.Entry)) and ('quantity' in str(i)):
                quantity = i.get()
                if Window.valid_quantity(self, quantity=quantity):
                    quantities.append(quantity)
        try:
            for i, val in enumerate(self.cart):
                self.cart[i].append(quantities[i])
        except:
            return tk.messagebox.showerror(message=f'Quantity must be integer. Enter correct quantities')
        action = tk.messagebox.askyesno(message=f'Save changes?')
        if action:
            models.Orders(order_id=self.order_id, customer_id=None).edit(customer_id=self.customer_id, cart=self.cart)
            tk.messagebox.showinfo(message=f'Order changed')
            Orders.show(self)
    def find(self, name, good, date, address):
        """
        Фильтрация заказов по параметрам
        Показывает в tree только заказы, соответсвующие фильтру

        :param name: имя клиента
        :param good: наименование товара
        :param date: дата создания заказа
        :param address: адрес доставки
        """
        Window.tree(self).destroy()
        query = db.Orders.find_query(self, name=name, good=good, date=date, address=address)
        Window.treeview(self, query)
        Orders.sort_tree(self)
class Customers():
    """
    Класс для построения виджетов для работы с клиентами

    Attributes:
        row - номер строки по умолчанию
        column - номер столбца по умолчанию
        query - текст запроса, возвращающего все данные из таблицы Customers (для tree)
    """
    def __init__(self):
        self.row = tk.IntVar(value=0)
        self.column = tk.IntVar(value=0)
        self.query = tk.StringVar(value='SELECT * FROM Customers')
    def show(self):
        """
        Удалает все виджеты
        Создает основные виджеты окна (main_widgets)
        Создает специфические для представления заказов виджеты:
            Window.tree на основе таблицы БД Customers
            create_button - кнопка для перехода в представление создания клиента
            edit_button - кнопка для перехода в представление редактирования клиента
            remove_button - кнопка удаления клиента (удаляется в текущем представлении)
            Виджеты для поиска клиента (find)
        """
        Window.clean_frame(self)
        Window.main_widgets(self)
        Window.treeview(self, query=Customers().query.get())
        Customers.sort_tree(self)
        self.create_button = tk.Button(master=self, name='create', text='New customer', width=15, command=lambda: Customers.create_frame(self))
        self.create_button.grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.edit_button = tk.Button(master=self, name='edit', text='Edit customer', width=15, command=lambda: Customers.edit_frame(self))
        self.edit_button.grid(row=2, column=1, sticky='w', padx=10, pady=10)
        self.remove_button = tk.Button(master=self, name='remove', text='Delete customer', width=15, command=lambda: Customers.remove(self))
        self.remove_button.grid(row=2, column=2, sticky='w', padx=10, pady=10)

        self.find_label = tk.Label(name='find_label', text='Filter customers', font='bold')
        self.find_label.grid(row=2, column=3, padx=10, pady=10, sticky='w')

        self.find_name_label = tk.Label(name='find_name_label', text='customer')
        self.find_name_label.grid(row=3, column=3, padx=10, pady=0, sticky='w')
        self.find_name_entry = tk.Entry(name='find_name_entry')
        self.find_name_entry.grid(row=3, column=4, padx=10, pady=0, sticky='w')

        self.find_contact_label = tk.Label(name='find_contact_label', text='contact')
        self.find_contact_label.grid(row=4, column=3, padx=10, pady=0, sticky='w')
        self.find_contact_entry = tk.Entry(name='find_good_entry')
        self.find_contact_entry.grid(row=4, column=4, padx=10, pady=0, sticky='w')

        self.find_address_label = tk.Label(name='find_address_label', text='address')
        self.find_address_label.grid(row=6, column=3, padx=10, pady=0, sticky='w')
        self.find_address_entry = tk.Entry(name='find_address_entry')
        self.find_address_entry.grid(row=6, column=4, padx=10, pady=0, sticky='w')

        self.find_button = tk.Button(name='find_button', text='Find', width=15, command=lambda: Customers.find(self,
                                                                                                            name=self.find_name_entry.get(),
                                                                                                            contact=self.find_contact_entry.get(),
                                                                                                            address=self.find_address_entry.get()
                                                                                                            ))
        self.find_button.grid(row=7, column=3, padx=10, pady=10, sticky='w')

        Window.deactivate(self, ['customers'])
    def sort_tree(self):
        """
        Назначает столбцам tree сортировку по клику на заголовки
        """
        Window.tree(self).heading(column='customer_id', command= lambda: Window.sortcolumn(self, col='customer_id', reverse=False))
        Window.tree(self).heading(column='name', command= lambda: Window.sortcolumn(self, col='name', reverse=False))
        Window.tree(self).heading(column='contact', command= lambda: Window.sortcolumn(self, col='contact', reverse=False))
        Window.tree(self).heading(column='address', command= lambda: Window.sortcolumn(self, col='address', reverse=False))
    def create_frame(self):
        """
        Удаляет виджеты поиска из окна
        Создает представление создания клиента:
             name_entry - поле ввода имени клиента
             contact_entry - поле ввода контакта клиента
             address_entry - поле ввода адреса клиента
             exit_button - кнопка возврата в представление Customers
             confirm_button - кнопка подтверждения изменений
        """
        for i in Window.winfo_children(self):
            i.destroy() if 'find' in str(i) else False

        self.name_label = tk.Label(text='name')
        self.name_label.grid(row=3, column=0, sticky='w', padx=10, pady=0)

        self.name_entry = tk.Entry(width=52, foreground='grey')
        self.name_entry.grid(row=3, column=1, sticky='w', padx=10, pady=0, columnspan=2)
        self.name_entry.insert(0, 'Enter customer name')
        self.name_entry.bind("<ButtonRelease-1>", lambda x: Window.activate_entry(self, self.name_entry))

        self.contact_label = tk.Label(text='contact')
        self.contact_label.grid(row=4, column=0, sticky='w', padx=10, pady=0)

        self.contact_entry = tk.Entry(width=52, foreground='grey')
        self.contact_entry.grid(row=4, column=1, sticky='w', padx=10, pady=0, columnspan=2)
        self.contact_entry.insert(0, 'Phone number in +7 format or e-mail')
        self.contact_entry.bind('<ButtonRelease-1>', lambda x: Window.activate_entry(self, self.contact_entry))

        self.address_label = tk.Label(text='address')
        self.address_label.grid(row=5, column=0, sticky='w', padx=10, pady=0)

        self.address_entry = tk.Entry(width=52, foreground='grey')
        self.address_entry.grid(row=5, column=1, sticky='w', padx=10, pady=0, columnspan=2)
        self.address_entry.insert(0, 'Enter customer address')
        self.address_entry.bind("<ButtonRelease-1>", lambda x: Window.activate_entry(self, self.address_entry))

        self.confirm_button = tk.Button(master=self, name='confirm', text='Create customer', width=15, command=lambda: Customers.create(self))
        self.confirm_button.grid(row=6, column=0, sticky='w', padx=10, pady=10)

        self.exit_button = tk.Button(master=self, name='exit', text='Exit', width=15, command=lambda: Customers.show(self))
        self.exit_button.grid(row=6, column=1, sticky='w', padx=10, pady=10)

        Window.deactivate(self, ['orders', 'customers', 'goods', 'analysis', 'admin', 'create', 'edit', 'remove'])
    def create(self):
        """
        Проверяет корректность введенных данных создает клиента
        """
        name = self.name_entry.get()
        contact = self.contact_entry.get()
        address = self.address_entry.get()
        if (
            Window.valid_name(self, name=name) and
            Window.valid_contact(self, contact=contact) and
            Window.valid_address(self, address=address)
            ):
            action = tk.messagebox.askyesno(message=f'Create customer {name}?')
            if action:
                models.Customers(customer_id=None, name=name, contact=contact, address=address).create()
                tk.messagebox.showinfo(message=f'Customer "{name}" created')
                Customers.show(self)
    def remove(self):
        """
        Удаляет клиента из БД
        """
        selection = Window.tree(self).selection()
        if selection == ():
            tk.messagebox.showwarning(message=f'Select customers to delete')
        else:
            action = tk.messagebox.askyesno(message='Do you want to delete selected customers and their orders from database?')
            if action:
                for i in selection:
                    customer_id = list(self.tree.item(i, 'values'))[0]
                    models.Customers(customer_id=customer_id, name=None, contact=None, address=None).remove()
                Customers.show(self)
    def edit_frame(self):
        """
        Удаляет виджеты поиска из окна
        Создает представление редактирования клиента:
        Текущая информация о клиенте
        new_name - поле ввода имени клиента
        new_contact - поле ввода контакта клиента
        new_address - поле ввода адреса клиента
        exit_button - кнопка возврата в представление Customers
        confirm_button - кнопка подтверждения изменений
        Если поле остается незаполненным, то этот атрибут не меняется
        """
        selection = Window.tree(self).selection()
        if len(selection) != 1:
            tk.messagebox.showwarning(message='Choose single customer')
        else:
            for i in Window.winfo_children(self):
                i.destroy() if 'find' in str(i) else False
            item = list(self.tree.item(selection, 'values'))
            self.customer_id = item[0]
            self.name = item[1]
            self.contact = item[2]
            self.address = item[3]
            tk.Label(name='customer customer_id label', text=f'customer_id: {self.customer_id}').grid(row=5, column=0, padx=10, pady=10, sticky='w')
            tk.Label(name='customer current title', text='Current', font='bold').grid(row=6, column=0, padx=10, pady=0, sticky='w')
            tk.Label(name='customer new title', text='New', font='bold').grid(row=6, column=1, padx=10, pady=0, sticky='w')

            tk.Label(name='customer name label', text=f'name: {self.name}', wraplength=100).grid(row=7, column=0, padx=10, pady=0, sticky='nw')
            tk.Label(name='customer contact label', text=f'contact: {self.contact}', wraplength=100).grid(row=8, column=0, padx=10, pady=0, sticky='nw')
            tk.Label(name='customer address label', text=f'address: {self.address}', wraplength=100).grid(row=9, column=0, padx=10, pady=0, sticky='nw')

            self.new_name = tk.Entry(name='customer name entry', width=52, foreground='grey')
            self.new_name.grid(row=7, column=1, padx=10, pady=0, sticky='nw', columnspan=2)
            self.new_name.insert(0, self.name)
            self.new_name.bind("<ButtonRelease-1>", lambda x: Window.activate_entry(self, self.new_name))

            self.new_contact = tk.Entry(name='customer contact entry', width=52, foreground='grey')
            self.new_contact.grid(row=8, column=1, padx=10, pady=0, sticky='nw', columnspan=2)
            self.new_contact.insert(0, self.contact)
            self.new_contact.bind("<ButtonRelease-1>", lambda x: Window.activate_entry(self, self.new_contact))

            self.new_address = tk.Entry(name='customer address entry', width=52, foreground='grey')
            self.new_address.grid(row=9, column=1, padx=10, pady=0, sticky='nw', columnspan=2)
            self.new_address.insert(0, self.address)
            self.new_address.bind('<ButtonRelease-1>', lambda x: Window.activate_entry(self, self.new_address))

            self.exit_button = tk.Button(master=self, name='exit', text='Exit', width=15, command=lambda: Customers.show(self))
            self.exit_button.grid(row=10, column=2, sticky='nw', padx=10, pady=10)
            self.confirm_button = tk.Button(name='confirm', text='Confirm', width=15, command=lambda: Customers.edit(self))
            self.confirm_button.grid(row=10, column=1, padx=10, pady=10, sticky='w')

            Window.deactivate(self, ['orders', 'customers', 'goods', 'analysis', 'admin', 'create', 'edit', 'remove'])
    def edit(self):
        """
        Проверяет корректность введенных данных и вносит изменения в клиента
        """
        new_name = self.new_name.get() if self.new_name.get() != '' else self.name
        new_contact = self.new_contact.get() if self.new_contact.get() != '' else self.contact
        new_address = self.new_address.get() if self.new_address.get() != '' else self.address
        if (
            Window.valid_name(self, name=new_name) and
            Window.valid_contact(self, contact=new_contact) and
            Window.valid_address(self, address=new_address)
            ):
            action = tk.messagebox.askyesno(message=f'Save changes in customer {self.name}, id {self.customer_id}?')
            if action:
                models.Customers(customer_id=self.customer_id, name=None, contact=None, address=None).edit(new_name=new_name, new_contact=new_contact, new_address=new_address)
                tk.messagebox.showinfo(message=f'Customer changed')
                Customers.show(self)
    def find(self, name, contact, address):
        """
        Фильтрация заказов по параметрам
        Показывает в tree только клиентов, соответсвующих фильтру

        :param name: имя клиента
        :param contact: контакт клиента
        :param address: адрес клиента
        """
        Window.tree(self).destroy()
        query = db.Customers.find_query(self, name=name, contact=contact, address=address)
        Window.treeview(self, query)
        Customers.sort_tree(self)
class Goods():
    def __init__(self):
        """
        Класс для построения виджетов для работы с товарами

        Attributes:
            row - номер строки по умолчанию
            column - номер столбца по умолчанию
            query - текст запроса, возвращающего все данные из таблицы Goods (для tree)
        """
        self.row = tk.IntVar(value=0)
        self.column = tk.IntVar(value=0)
        self.query = tk.StringVar(value='SELECT * FROM Goods')
    def show(self):
        """
        Удалает все виджеты
        Создает основные виджеты окна (main_widgets)
        Создает специфические для представления товаров виджеты:
            Window.tree на основе таблицы БД Goods
            create_button - кнопка для перехода в представление создания товара
            edit_button - кнопка для перехода в представление редактирования товара
            remove_button - кнопка удаления товара (удаляется в текущем представлении)
            Виджеты для поиска клиента (find)
        """
        Window.clean_frame(self)
        Window.main_widgets(self)
        Window.treeview(self, query=Goods().query.get())
        Goods.sort_tree(self)
        self.create_button = tk.Button(master=self, name='create', text='New good', width=15, command=lambda: Goods.create_frame(self))
        self.create_button.grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.edit_button = tk.Button(master=self, name='edit', text='Edit good', width=15,
                                       command=lambda: Goods.edit_frame(self))
        self.edit_button.grid(row=2, column=1, sticky='w', padx=10, pady=10)
        self.remove_button = tk.Button(master=self, name='remove', text='Delete good', width=15,
                                       command=lambda: Goods.remove(self))
        self.remove_button.grid(row=2, column=2, sticky='w', padx=10, pady=10)

        self.find_label = tk.Label(name='find_label', text='Filter goods', font='bold')
        self.find_label.grid(row=2, column=3, padx=10, pady=10, sticky='w')

        self.find_good_label = tk.Label(name='find_good_label', text='good')
        self.find_good_label.grid(row=3, column=3, padx=10, pady=0, sticky='w')
        self.find_good_entry = tk.Entry(name='find_good_entry')
        self.find_good_entry.grid(row=3, column=4, padx=10, pady=0, sticky='w')

        self.find_minprice_label = tk.Label(name='find_minprice_label', text='min price')
        self.find_minprice_label.grid(row=4, column=3, padx=10, pady=0, sticky='w')
        self.find_minprice_entry = tk.Entry(name='find_minprice_entry')
        self.find_minprice_entry.grid(row=4, column=4, padx=10, pady=0, sticky='w')

        self.find_maxprice_label = tk.Label(name='find_maxprice_label', text='max price')
        self.find_maxprice_label.grid(row=6, column=3, padx=10, pady=0, sticky='w')
        self.find_maxprice_entry = tk.Entry(name='find_maxprice_entry')
        self.find_maxprice_entry.grid(row=6, column=4, padx=10, pady=0, sticky='w')

        self.find_button = tk.Button(name='find_button', text='Find', width=15, command=lambda: Goods.find(self,
                                                                                                               good=self.find_good_entry.get(),
                                                                                                               minprice=self.find_minprice_entry.get(),
                                                                                                               maxprice=self.find_maxprice_entry.get()
                                                                                                               ))
        self.find_button.grid(row=7, column=3, padx=10, pady=10, sticky='w')
        Window.deactivate(self, ['goods'])
    def create_frame(self):
        """
        Удаляет виджеты поиска из окна
        Создает представление создания товара:
             good_entry - поле ввода наименования товара
             price_entry - поле ввода цены товара
             exit_button - кнопка возврата в представление Goods
             confirm_button - кнопка подтверждения изменений
        """
        for i in Window.winfo_children(self):
            i.destroy() if 'find' in str(i) else False
        self.good_label = tk.Label(text='good')
        self.good_label.grid(row=3, column=0, sticky='w', padx=10, pady=0)
        self.good_entry = tk.Entry()
        self.good_entry.grid(row=3, column=1, sticky='w', padx=10, pady=0)
        self.price_label = tk.Label(text='price')
        self.price_label.grid(row=4, column=0, sticky='w', padx=10, pady=0)
        self.price_entry = tk.Entry()
        self.price_entry.grid(row=4, column=1, sticky='w', padx=10, pady=0)
        self.confirm_button = tk.Button(master=self, name='confirm', text='Create good', width=15,
                                       command=lambda: Goods.create(self))
        self.confirm_button.grid(row=5, column=0, sticky='w', padx=10, pady=10)
        self.exit_button = tk.Button(master=self, name='exit', text='Exit', width=15,
                                     command=lambda: Goods.show(self))
        self.exit_button.grid(row=5, column=1, sticky='w', padx=10, pady=10)
        Window.deactivate(self, ['orders', 'customers', 'goods', 'analysis', 'admin', 'create', 'edit', 'remove'])
    def create(self):
        """
        Проверяет корректность введенных данных создает клиента
        """
        good = self.good_entry.get()
        price = self.price_entry.get()
        if (
            Window.valid_good(self, good=good) and
            Window.valid_price(self, price=price)
            ):
            action = tk.messagebox.askyesno(message=f'Create new good "{good}"?')
            if action:
                models.Goods(good_id=None, good=good, price=price).create()
                tk.messagebox.showinfo(message=f'Good "{good}" created')
                Goods.show(self)
    def remove(self):
        """
        Удаляет товар из БД
        """
        selection = Window.tree(self).selection()
        if selection == ():
            tk.messagebox.showwarning(message=f'Select goods to delete')
        else:
            action = tk.messagebox.askyesno(message=f'Do you want to delete selected goods and all orders containing it from database?')
            if action:
                for i in selection:
                    good_id = list(self.tree.item(i, 'values'))[0]
                    models.Goods(good_id=good_id, good=None, price=None).remove()
                tk.messagebox.showinfo(message=f'Good deleted')
                Goods.show(self)
    def edit_frame(self):
        """
        Удаляет виджеты поиска из окна
        Создает представление редактирования товара:
        Текущая информация о товаре
        new_good - поле ввода нового наименования товара
        new_price - поле ввода новой цены товара
        exit_button - кнопка возврата в представление Customers
        confirm_button - кнопка подтверждения изменений
        Если поле остается незаполненным, то этот атрибут не меняется
        """
        selection = Window.tree(self).selection()
        if len(selection) != 1:
            tk.messagebox.showwarning(message='Choose single good')
        else:
            for i in Window.winfo_children(self):
                i.destroy() if 'find' in str(i) else False
            item = list(self.tree.item(selection, 'values'))
            self.good_id = item[0]
            self.good = item[1]
            self.price = item[2]

            tk.Label(name='good good_id label', text=f'good_id:   {self.good_id}').grid(row=5, column=0, padx=10, pady=10, sticky='w')
            tk.Label(name='good current title', text='Current', font='bold').grid(row=6, column=0, padx=10, pady=0, sticky='w')
            tk.Label(name='good new title', text='New', font='bold').grid(row=6, column=1, padx=10, pady=0, sticky='w')

            tk.Label(name='good good label', text=f'good:       {self.good}').grid(row=7, column=0, padx=10, pady=0, sticky='w')
            tk.Label(name='good price label', text=f'price:        {self.price}').grid(row=8, column=0, padx=10, pady=0, sticky='w')

            self.new_good = tk.Entry(name='good good entry')
            self.new_good.grid(row=7, column=1, padx=10, pady=0, sticky='w')
            self.new_price = tk.Entry(name='good price entry')
            self.new_price.grid(row=8, column=1, padx=10, pady=0, sticky='w')

            tk.Button(master=self, name='confirm', text='Confirm', width=15, command=lambda: Goods.edit(self)).grid(row=9, column=1, padx=10, pady=10, sticky='w')
            tk.Button(master=self, name='exit', text='Exit', width=15, command=lambda: Goods.show(self)).grid(row=9, column=2, sticky='w', padx=10, pady=10)

            Window.deactivate(self, ['orders', 'customers', 'goods', 'analysis', 'admin', 'create', 'edit', 'remove'])
    def edit(self):
        """
        Проверяет корректность введенных данных и вносит изменения в товар
        """
        new_good = self.new_good.get() if self.new_good.get() != '' else self.good
        new_price = self.new_price.get() if self.new_price.get() != '' else self.price
        if (
            Window.valid_good(self, name=new_good) and
            Window.valid_price(self, value=new_price)
            ):
            action = tk.messagebox.askyesno(message=f'Save changes in good "{self.good}"?')
            if action:
                models.Goods(good_id=self.good_id, good=None, price=None).edit(new_good=new_good, new_price=new_price)
                tk.messagebox.showinfo(message=f'Good "{self.good}" changed')
                Goods.show(self)
    def sort_tree(self):
        """
        Назначает столбцам tree сортировку по клику на заголовки
        """
        Window.tree(self).heading(column='good_id', command= lambda: Window.sortcolumn(self, col='good_id', reverse=False))
        Window.tree(self).heading(column='good', command= lambda: Window.sortcolumn(self, col='good', reverse=False))
        Window.tree(self).heading(column='price', command= lambda: Window.sortcolumn(self, col='price', reverse=False))
    def find(self, good, minprice, maxprice):
        """
            Фильтрация товаров по параметрам
            Показывает в tree только товары, соответсвующие фильтру

            :param good: наименование товара
            :param minprice: минимальная цена товара. Если не заполнено, принимается равной 0
            :param maxprice: минимальная цена товара. Если не заполнено, принимается равным максимальной цене товара в БД
            """
        Window.tree(self).destroy()
        query = db.Goods.find_query(self, good=good, minprice=minprice, maxprice=maxprice)
        Window.treeview(self, query)
        Goods.sort_tree(self)
class Analysis():
    """
    Класс для построения аналитических виджетов
    """
    def show(self):
        """
        Удалает все виджеты
        Создает основные виджеты окна анализа:
        top_button - кнопка вызова Tree с топ-5 покупателей по продажам
        dinamycs_button - кнопка вызова графиков продаж
        relations_button - кнопка вызова графа связей между клиентами по заказанным товарам
        exit_button - возврат в представление Window.main_widgets
        """
        Window.clean_frame(self)

        self.top_button = tk.Button(name='top', text='Top 5 customers', width=25, height=3, background='white', command=lambda: Analysis.top(self))
        self.top_button.grid(row=0, column=0, padx=50, pady=10, sticky='w')

        self.dinamycs_button = tk.Button(name='dinamycs', text='Sales dinamycs', width=25, height=3, background='white', command=lambda: Analysis.dinamics(self))
        self.dinamycs_button.grid(row=0, column=1, padx=50, pady=10, sticky='w')

        self.relations_button = tk.Button(name='relations', text='Relations', width=25, height=3, background='white', command=lambda: Analysis.relations(self))
        self.relations_button.grid(row=0, column=2, padx=50, pady=10, sticky='w')

        self.exit_button = tk.Button(name='exit', text='To main page', width=15, height=1, background='lightgrey', command=lambda: Orders.show(self))
        self.exit_button.grid(row=0, column=3, padx=50, pady=10, sticky='ew')
    def top(self):
        """
        Показывает Tree с топ-5 покупателей по продажам
        """
        Analysis.show(self)
        Window.treeview(self, analysis.topquery())
        Window.tree(self).config(height=5)
    def dinamics(self):
        """
        Показывает графиуи продаж
        """
        Analysis.show(self)
        canvas = analysis.dinamics(self)
        widget = canvas.get_tk_widget()
        widget.grid(row=1, column=0, padx=10, pady=10, columnspan=4)  # Размещаем холст в окне
    def relations(self):
        """
        Создает Tree c выбором клиентов для построения графа
        """
        Analysis.show(self)
        Window.treeview(self, '''SELECT * FROM Customers''')
        Customers.sort_tree(self)
        tk.Button(text='Show relations', width=15, height=3, command=lambda: select_customers()).grid(row=2, column=0, padx=30, pady=10, sticky='w')
        def select_customers():
            """
            Формирует граф связей между выбранными клиентами по заказанным товарам
            """
            selection = self.tree.selection()
            if len(selection) <= 1:
                return tk.messagebox.showerror(message='Select 2 or more customers')
            selected_customers = tuple([int(self.tree.item(i, 'values')[0]) for i in selection])
            canvas = analysis.relations(self, selected_customers)
            widget = canvas.get_tk_widget()
            widget.grid(row=3, column=0, padx=10, pady=10, columnspan=4)  # Размещаем холст в окне
class Admin(Window):
    def __init__(self):
        """
        Класс для управления БД посредством импорта и экспорта файлов
        """
        super().__init__()
        self.title('Admin')
        self.geometry('800x600')
        self.attributes('-fullscreen', False)
        self.bind('<Escape>', self.exit_fullscreen)
    def main_widgets(self):
        """
        Основные виджеты рабочего окна (присутствуют во всех представлениях окна):
            Кнопка "Orders" - импорт заказов
            Кнопка "Customers" - импорт клиентов
            Кнопка "Goods" - импорт товаров
            text - поле ввода пользовательского sql запроса
            export_csv_button - кнопка экспорта данных в формате csv
            export_json_button - кнопка экспорта данных в формате json
        """
        self.clean_frame()
        self.import_customers_button = tk.Button(master=self,
                                                 name='import_customers_button',
                                                 text='Import\ncustomers',
                                                 width=15,
                                                 height=3,
                                                 command=lambda: self.importfile(
                                                     attr='Customers',
                                                     filename='customers',
                                                     deactbutton=['import_customers_button'],
                                                     column=0)
                                                 )
        self.import_customers_button.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        self.import_goods_button = tk.Button(master=self,
                                             name='import_goods_button',
                                             text='Import\ngoods',
                                             width=15,
                                             height=3,
                                             command=lambda: self.importfile(
                                                 attr='Goods',
                                                 filename='goods',
                                                 deactbutton=['import_goods_button'],
                                                 column=2)
                                             )
        self.import_goods_button.grid(row=0, column=2, padx=10, pady=10, columnspan=2)
        self.import_orders_button = tk.Button(master=self,
                                              name='import_orders_button',
                                              text='Import\norders',
                                              width=15,
                                              height=3,
                                              command=lambda: self.importfile(
                                                 attr='Orders',
                                                 filename='orders',
                                                 deactbutton=['import_orders_button'],
                                                 column=4)
                                              )
        self.import_orders_button.grid(row=0, column=4, padx=10, pady=10, columnspan=2)
        self.text = tk.Text(self, width=48, height=20, wrap='word')  # wrap="word" для переноса по словам
        self.text.grid(row=3, column=0, padx=10, pady=10, columnspan=7)
        self.text.bind('<ButtonRelease-1>', lambda x: self.destroy_import())
        self.export_csv_button = tk.Button(master=self, name='export_csv_button', text='Export csv', width=15, height=3, command=self.export_csv, state=tk.ACTIVE)
        self.export_csv_button.grid(row=4, column=0, padx=10, pady=10, columnspan=2)
        self.export_json_button = tk.Button(master=self, name='export_json_button', text='Export json', width=15, height=3,
                                           command=self.export_json, state=tk.ACTIVE)
        self.export_json_button.grid(row=4, column=2, padx=10, pady=10, columnspan=2)
        self.export_filename = tk.Entry(self, name='filename', width=42)
        self.export_filename.grid(row=5, column=0, padx=10, pady=10, columnspan=4, sticky='w')
        self.export_filename.insert(0, 'report')
    def importfile(self, attr, filename, deactbutton, column):
        """
        Создает виджеты для импорта файла
        В зависимости от нажатой кнопки в основном окне положение и функции виджетов отличвются
        :param attr: категория данных (Orders, Customers, Goods), (str)
        :param filename: название импортируемого файла
        :param deactbutton: имя кнопки, которая становится неактивной
        :param column: номер столбца в grid
        Виджеты:
            csv - кнопка импорта из csv
            json - кнопка импорта из json
            file - поле ввода названия файла
        """
        self.attr = attr
        self.main_widgets()
        self.deactivate(deactbutton)
        self.csv = tk.Button(master=self, name='csv', text='csv', width=5, height=1, command=self.import_csv)
        self.csv.grid(row=1, column=column, padx=10, pady=10, sticky='e')
        self.json = tk.Button(master=self, name='json', text='json', width=5, height=1, command=self.import_json)
        self.json.grid(row=1, column=column+1, padx=10, pady=10, sticky='w')
        self.file = tk.Entry(master=self, width=18, foreground='black')
        self.file.grid(row=2, column=column, columnspan=2)
        # self.file.bind('<ButtonRelease-1>', lambda x: Window.activate_entry(self, self.file))
        self.file.insert(0, filename)
        self.export_csv_button.config(state=tk.DISABLED)
        self.export_json_button.config(state=tk.DISABLED)
        try:
            self.export_filename.destroy()
        except:
            pass
    def import_csv(self):
        """
        Загружает в БД файл csv
        """
        funcs = {
                'Customers': admin.import_customers_csv,
                'Goods': admin.import_goods_csv,
                'Orders': admin.import_orders_csv
                }
        f = funcs.get(self.attr)
        try:
            filename = self.file.get() + '.csv'
            f(filename)
            tk.messagebox.showinfo(title='Import', message='File imported sucsessfully')
            self.destroy()
        except:
            tk.messagebox.showerror(title='Error', message='File not found or is not valid')
    def import_json(self):
        """
        Загружает в БД файл json
        """
        funcs = {
                'Customers': admin.import_customers_json,
                'Goods': admin.import_goods_json,
                'Orders': admin.import_orders_json
                }
        f = funcs.get(self.attr)
        try:
            filename = self.file.get() + '.json'
            f(filename)
            tk.messagebox.showinfo(title='Export', message='File imported sucsessfully')
            self.destroy()
        except:
            tk.messagebox.showerror(title='Error', message='File not found or is not valid')
    def export_csv(self):
        """
        Выгружает пользрвательский запрос в формате csv
        """
        filename = self.export_filename.get() + '.csv'
        query = self.text.get('1.0', tk.END)
        try:
            admin.export_csv(query, filename)
            tk.messagebox.showinfo(message='File exported successfully')
            self.destroy()
        except:
            tk.messagebox.showerror(title='Error', message='Query could not be completed')
    def export_json(self):
        """
        Выгружает пользрвательский запрос в формате json
        """
        filename = self.export_filename.get() + '.json'
        query = self.text.get('1.0', tk.END)
        try:
            admin.export_json(query, filename)
            tk.messagebox.showinfo(message='File exported successfully')
            self.destroy()
        except:
            tk.messagebox.showerror(title='Error', message='Query could not be completed')
    def destroy_import(self):
        """
        Удаляет виджеты импорта и делает поле ввода запроса активным
        """
        self.export_csv_button.config(state=tk.ACTIVE)
        self.export_json_button.config(state=tk.ACTIVE)
        try:
            self.csv.destroy()
            self.json.destroy()
            self.file.destroy()
        except:
            pass
        self.import_customers_button.config(state=tk.ACTIVE)
        self.import_goods_button.config(state=tk.ACTIVE)
        self.import_orders_button.config(state=tk.ACTIVE)
        self.export_filename = tk.Entry(self, name='filename', width=42)
        self.export_filename.grid(row=5, column=0, padx=10, pady=10, columnspan=4, sticky='w')
        self.export_filename.insert(0, 'report')
