from Node import Node
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
    def __init__(self, population: List[Node]) -> None:
        self.sequence = np.random.permutation(population)
        self.routes = []
        self.fitness = -1
        self.generate_entire_routes() # overrides self.routes
        self.calculate_fitness() # overrides self.fitness

    def generate_entire_routes(self):
        subroute = []
        capacity_sum = 0
        for n in self.sequence:
            if capacity_sum + n.demand <= 25:
                subroute.append(n)
                capacity_sum += n.demand
            else:
                self.routes.append(subroute)
                capacity_sum = n.demand
                subroute = [n]
        self.routes.append(subroute)
    
    def calculate_fitness(self):
        total_distance = np.sum([self._subroute_distance(subroute) for subroute in self.routes])
        self.fitness = 1/total_distance*1073 # normalize fitness (0, 1]


    def _subroute_distance(self, subroute):
        subroute = [depot_node] + subroute + [depot_node]
        subroute_distance = 0
        for i in range(len(subroute) - 1):
            start_node = subroute[i]
            goal_node_id = subroute[i+1].node_id
            subroute_distance += start_node.distances[goal_node_id]
        return subroute_distance






if __name__=="__main__":
    pass
    # l = customer_list
    # print(l)
    # c = Chromosome(l)
    # print(c.sequence)
    # print(c.routes)
    # print(len(c.routes))

    # # measuring initialization speed
    # start_time = time()
    # for i in range(10000):
    #     c = Chromosome(customer_list)
    #     # print(c.fitness)
    # print(time() - start_time)