from Node import Node
from typing import List

import numpy as np
import csv

with open("data.csv", newline='') as r:
    reader = csv.reader(r, delimiter=";")
    data = np.array(list(reader)[1:], dtype = np.int64)

node_list = [Node(node_id, demand, x, y) for node_id, demand, x, y in data]
depot_node = node_list[0]
customer_list = node_list[1:]

class Chromosome:
    def __init__(self, population: List[Node]) -> None:
        self.sequence = np.random.permutation(population)
        self.routes = []
        self.generate_entire_routes()

    def generate_entire_routes(self):
        subroute = []
        capacity_sum = 0
        for n in self.sequence:
            if capacity_sum + n.demand <= 100:
                subroute.append(n)
                capacity_sum += n.demand
            else:
                self.routes.append(subroute)
                capacity_sum = 0
                subroute = [n]
        self.routes.append(subroute)



# if __name__=="__main__":
#     l = customer_list[:10]
#     print(l)
#     c = Chromosome(l)
#     print(c.sequence)
#     print(c.routes)
#     print(len(c.routes))