from collections import defaultdict
import numpy as np
import sys


FOLDER_INPUT_NAME = 'csv_input'
FOLDER_OUTPUT_NAME = 'csv_output'

# column number
START_LON = 2
START_LAT = 3
END_LON = 5
END_LAT = 6


class Node:
    def __init__(self, index=-1, x1=0, x2=90):
        self.index = index
        self.x1 = x1
        self.x2 = x2
        self.parents = []
        self.children = []

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
        return parent.x1 <= self.x1 and \
            self.x2 <= parent.x2

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

def main():
    if len(sys.argv) == 1:
        return

    filename = sys.argv[1]
    input_path = '{0}/{1}'.format(FOLDER_INPUT_NAME, filename)
    data = np.genfromtxt(input_path, skip_header=1, delimiter=',')

    output = defaultdict(Node)
    for i, row in enumerate(data):
        x1 = row[START_LAT]
        y1 = row[START_LON]
        x2 = row[END_LAT]
        y2 = row[END_LON]


        # уравнение Ax + By + C = 0, a = 1
        b = 0
        if y1 != y2:
            b = (x2 - x1) / (y1 - y2)
        c = -x1 - b * y1

        new_node = Node(i, x1, x2)
        key = (b, c)
        root = output[key]
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