from data_structures import Node, Route
from typing import List
from time import time

import numpy as np
import csv

with open("data.csv", newline='') as r:
    reader = csv.reader(r, delimiter=";")
    data = np.array(list(reader)[1:], dtype = np.int64)

node_list = [Node(node_id, demand, x, y) for node_id, demand, x, y in data]
depot_node = node_list[0]
customer_list = node_list[1:]

for start_node in node_list:
    for goal_node in node_list:
        x1, y1, x2, y2 = [start_node.x, start_node.y, goal_node.x, goal_node.y]
        start_node.distances[goal_node.node_id] = ((x1 - x2)**2 + (y1 - y2)**2)**0.5

class Chromosome:
    def __init__(self, node_list: List[Node]) -> None:
        self.sequence = np.random.permutation(node_list)
        self.routes = []
        self.fitness = -1
        self.generate_entire_routes() # overrides self.routes
        self.calculate_fitness() # overrides self.fitness

    def generate_entire_routes(self):
        subroute = []
        capacity_sum = 0
        for n in self.sequence:
            if capacity_sum + n.demand <= 100:
                subroute.append(n)
                capacity_sum += n.demand
            else:
                self.routes.append(Route(subroute, capacity_sum, depot_node))
                capacity_sum = n.demand
                subroute = [n]
        self.routes.append(Route(subroute, capacity_sum, depot_node))
    
    def calculate_fitness(self):
        total_distance = sum([route.route_distance for route in self.routes])
        self.fitness = 1/total_distance*1073 # normalize fitness (0, 1]

    def __mul__(self, other): # crossover operation
        pass

    def mutation(self):
        # after overriding self.routes, self._flatten_routes is called to update self.sequence
        self._flatten_routes()

    def _flatten_routes(self):
        new_sequence = []
        for subroute in self.routes:
            new_sequence += subroute
        self.sequence = new_sequence

if __name__=="__main__":
    pass
    l = customer_list
    print(l)
    print()
    c = Chromosome(l)
    print(c.sequence)
    print()
    print(c.routes)
    print()
    print(len(c.routes))
    print()

    for route in 

    # # measuring initialization speed
    # start_time = time()
    # max_fitness = 0
    # min_fitness = 1
    # for i in range(10000):
    #     c = Chromosome(customer_list)
    #     max_fitness = max(max_fitness, c.fitness)
    #     min_fitness = min(min_fitness, c.fitness)
    # print(time() - start_time)
    # print(max_fitness, min_fitness)