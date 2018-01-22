from collections import defaultdict
import math
import numpy as np
import sys


FOLDER_INPUT_NAME = 'csv_input'
FOLDER_OUTPUT_NAME = 'csv_output'

# column number
START_LON = 2
START_LAT = 3
END_LON = 5
END_LAT = 6

RADIUS = 6371000
PI = 3.1415926

class Node:
    def __init__(self, index=-1, start_longitude=0, start_latitude=0, end_longitude=0, end_latitude=0, start=0, end=0, direction=True):
        self.index = index
        self.start_longitude = start_longitude
        self.start_latitude = start_latitude
        self.end_longitude = end_longitude
        self.end_latitude = end_latitude
        self.parents = []
        self.children = []
        self.start = start
        self.end = end
        self.direction = direction

    def get_all_children(self):
        result = list(self.children)
        for child in self.children:
            grand_children = child.get_all_children()
            if len(grand_children) > 0:
                result += grand_children
        return result

    def find_all_child(self, new_node):
        result = []
        if self.is_child_to(new_node):
            self.parents.append(new_node)
            result.append(self)
        else:
            for child in self.children:
                result += child.find_available_child(new_node)
        return result

    def is_child_to(self, parent):
        # не одно направление движения
        if self.direction != parent.direction:
            return False
        return parent.direction and \
            parent.start <= self.start and \
            self.end <= parent.end or \
            not parent.direction and \
            self.start <= parent.start and \
            parent.end <= self.end

    def insert_node(self, new_node):
        if new_node.is_child_to(self):
            need_append = True
            for child in self.children:
                insert_result = child.insert_node(new_node)
                if insert_result:
                    need_append = False
            if need_append:
                new_node.parents.append(self)
                children_nodes_for_new_node = []
                for child in self.children:
                    children_nodes_for_new_node += child.find_all_child(new_node)
                new_node.children += children_nodes_for_new_node
                self.children.append(new_node)
            return True
        if self.is_child_to(new_node):
            new_node.children.append(self)
            parents = self.parents
            self.parents = [new_node]
            for parent in parents:
                parent.children.remove(self)
                parent.insert_node(new_node)
            return True
        return False

    def print_node(self, tabs=0):
        s = ' ' * tabs
        print(s, self)
        for child in self.children:
            child.print_node(tabs + 2)

    def write_output(self, data):
        result = []
        if self.index != -1:
            for child in self.get_all_children():
                row_result = list(data[self.index]) + list(data[child.index])
                result.append(row_result)
        for child in self.children:
            child_result = child.write_output(data)
            if len(child_result) > 0:
                result += child_result
        return result

    def __str__(self):
        return str('{}; x1 = {}; x2 = {}'.format(self.index, self.x1, self.x2))


def sign(x):
    if x > 0: return 1
    elif x < 0: return -1
    return x


class RootNode(Node):
    def __init__(self):
        super(RootNode, self).__init__()
        self.start = 0
        self.end = 360

    def calculate_degrees(self, long, lat):
        """ Метод для вычисления угла между фиксированной точкой и любой точкой, лежащей в этой плоскости """
        delta_longitude = long - self.fixed_longitude
        delta_latitude = lat - self.fixed_latitude
        k = PI / 180 # для перевода градусов в радианы
        # теорема косинусов для сферических координат
        cos_value = math.cos(delta_latitude * k) * math.cos(delta_longitude * k)
        alpha = math.acos(cos_value)
        alpha *= sign(delta_longitude)
        return alpha

    def insert_node(self, new_node):
        # если это первая Node, то нужно зафиксировать стартовую точку как начало координат
        if len(self.children) == 0:
            self.fixed_longitude = new_node.start_longitude
            self.fixed_latitude = new_node.start_latitude
        # запоминаем отклонения от фиксированной точки
        new_node.start = self.calculate_degrees(new_node.start_longitude, new_node.start_latitude)
        new_node.end = self.calculate_degrees(new_node.end_longitude, new_node.end_latitude)
        # Если путь диаметрально противоположный, то существует выбор движения
        if new_node.end - new_node.start == 180:
            other_node = Node(index=new_node.index, start=new_node.start, end=new_node.end, direction=False)
            super(RootNode, self).insert_node(other_node)
        super(RootNode, self).insert_node(new_node)


def calculate_spherical_coordinates(phi, teta, r=RADIUS):
    x = r * math.sin(teta) * math.cos(phi)
    y = r * math.sin(teta) * math.sin(phi)
    z = r * math.cos(teta)
    return (x, y, z)


def main():
    if len(sys.argv) == 1:
        return

    filename = sys.argv[1]
    input_path = '{0}/{1}'.format(FOLDER_INPUT_NAME, filename)
    data = np.genfromtxt(input_path, skip_header=1, delimiter=',')

    output = defaultdict(RootNode)
    for i, row in enumerate(data):
        start_latitude = row[START_LAT]
        start_longitude = row[START_LON]
        end_latitude = row[END_LAT]
        end_longitude = row[END_LON]

        # перейдём к сферическим координатами и найдём x,y,z, зная углы phi, teta
        # phi - это значение longitude
        # teta - это 90 - значение latitude
        phi = start_longitude
        teta = 90 - start_latitude
        start_x, start_y, start_z = calculate_spherical_coordinates(phi, teta)

        phi = end_longitude
        teta = 90 - end_latitude
        end_x, end_y, end_z = calculate_spherical_coordinates(phi, teta)

        # строим плоскость по 3 точкам start, end и O - начальная точка с координатами 0,0,0
        # Уравнение плоскости A(x-x0) + B(y-y0) + C(z-z0) = 0
        # x0 = y0 = z0 = 0
        a = start_y * end_z - end_y * start_z
        b = start_x * end_z - end_x * start_z
        c = start_x * end_y - end_x * start_y

        # Пусть все коэффициент перед X будет положительным
        if a < 0:
            a *= -1
            b *= -1
            c *= -1

        key = (a, b, c)
        root = output[key]
        new_node = Node(i, start_longitude, start_latitude, end_longitude, end_latitude)
        root.insert_node(new_node)

    result = []
    for k, v in output.items():
        node_result = v.write_output(data)
        if len(node_result) > 0:
            result += node_result

    fields = 'route_id,step_id,start_lon,start_lat,start_time,end_lon,end_lat,end_time,travel_mode,age_group,foreign'.split(',')
    prefixes = ('parent_','child_')
    header_fields = [prefix + field
                     for prefix in prefixes
                     for field in fields]
    header = ','.join(header_fields)

    output_path = '{0}/{1}'.format(FOLDER_OUTPUT_NAME, filename)
    with open(output_path, 'wb') as fp:
        fp.write((header + '\n').encode())
        np_result = np.array(result)
        np.savetxt(fp, np_result, fmt='%.4f')

if __name__ == '__main__':
    main()