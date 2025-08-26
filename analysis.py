import matplotlib.pyplot as plt
import networkx as nx
import db
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
def fig(frame):
        """
        Создает фигуру для дальнейшего ее размещения в окне tkinter

        :param frame: окно, в котором размещается фигура
        :return: Фигура без какого-либо содержания
        """
        fig = plt.figure(figsize=(10, 5))
        figura = FigureCanvasTkAgg(fig, master=frame)
        return figura
def topquery():
        """
        Запрос, выводящий топ-5 клиентов по сумме покупок

        :return: текст запроса
        """
        query = f'''
                SELECT
                    Customers.name AS customer,
                    SUM(price * quantity) AS sales,
                    COUNT(DISTINCT(Orders.order_id)) AS orders,
                    SUM(quantity) AS goods
                FROM Customers
                JOIN Orders ON Customers.customer_id = Orders.customer_id
                JOIN Order_details ON Orders.order_id = Order_details.order_id
                JOIN Goods ON Order_details.good_id = Goods.good_id
                GROUP BY Customers.name
                ORDER BY sales DESC
                LIMIT 5
                '''
        return query
def dinamicsdata():
        """
        Запрос, возвращающий данные для построения диаграмм динамики продаж

        :return: результат выполнения запроса (DataFrame)
        """
        query = f'''
                        SELECT
                            date,
                            COUNT(DISTINCT(Orders.order_id)) AS orders,
                            SUM(price * quantity) AS sales
                        FROM Orders
                        JOIN Order_details ON Orders.order_id = Order_details.order_id
                        JOIN Goods ON Order_details.good_id = Goods.good_id
                        GROUP BY date
                        '''
        data = db.Connection().to_df(query)
        return data
def relationsdata(selected_customers):
        """
        Запрос, возвращающий данные для построения графа связей между клиентами по заказанным товарам

        :param selected_customers:
        :return: результат выполнения запроса (numpy array)
        """
        query = f'''
                        WITH right AS 
                        (SELECT DISTINCT
                            Customers.name AS name,
                            Order_details.good_id AS good_id
                        FROM Customers
                        LEFT JOIN Orders ON Customers.customer_id = Orders.customer_id
                        LEFT JOIN Order_details ON Orders.order_id = Order_details.order_id
                        WHERE Customers.customer_id IN {selected_customers})

                        SELECT DISTINCT
                            Customers.name AS customer,
                            right.name AS follower
                        FROM Customers
                        LEFT JOIN Orders ON Customers.customer_id = Orders.customer_id
                        LEFT JOIN Order_details ON Orders.order_id = Order_details.order_id 
                        LEFT JOIN right ON Order_details.good_id = right.good_id AND Customers.name <> right.name
                        WHERE Customers.customer_id IN {selected_customers}
                        '''
        data = db.Connection().to_df(query)
        data = data.to_numpy()
        return data
def top():
        """
        Преобразование запроса topquery в DataFrame

        :return: результат выполнения запроса (DataFrame)
        """
        data = db.Connection().to_df(topquery())
        return data
def dinamics(frame):
        """
        Формирует графики количества заказов и суммы продаж по датам

        :param frame: окно, в котором размещаются графики
        :return: Фигура с графиками количества заказов и суммы продаж по датам
        """
        data = dinamicsdata()
        figura = fig(frame)

        '''левый график — количество заказов по датам'''
        plt.subplot(2, 1, 1) # 1 row, 2 columns, 1 plot
        plt.plot(data['date'].values, data['orders'].values, color='red')
        plt.xticks(rotation=90)
        plt.title('Orders')
        plt.xlabel('date')
        plt.grid(axis='both', which='major', linestyle='dotted', linewidth=0.5)
        '''правый график — сумма продаж по датам'''
        plt.subplot(2, 1, 2) # 1 row, 2 columns, 2 plot
        plt.plot(data['date'].values, data['sales'].values, color='blue')
        plt.xticks(rotation=90)
        plt.title('Sales')
        plt.xlabel('date')
        plt.grid(axis='both', which='major', linestyle='dotted', linewidth=0.5)
        '''выводим оба графика'''
        plt.tight_layout()
        return figura
def relations(frame, selected_customers):
        """
        Формирует граф связей между клиентами по общим товарам в заказах
        Если общих товаров нет, клиент показан узлом, не связанным с другими узлами

        :param frame: окно, в котором размещается граф
        :param selected_customers: выбранные клиенты ([customer_id, name, contact, address], ...)
        :return: Фигура с графом
        """
        data = relationsdata(selected_customers)
        figura = fig(frame)
        G = nx.Graph()
        for i in data:
            G.add_node(i[0])
            if i[1] != None:
                G.add_node(i[1])
                G.add_edge(i[0], i[1])
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=300)  # Узлы
        nx.draw_networkx_edges(G, pos, edge_color='black', width=1)  # Ребра
        nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
        return figura
