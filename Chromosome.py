from data_structures import Node, Route
from typing import List
from copy import deepcopy
from time import time

import numpy as np
import csv

with open("data.csv", newline='') as r:
    reader = csv.reader(r, delimiter=";")
    data = np.array(list(reader)[1:], dtype = np.int64)

node_list = [Node(node_id, demand, x, y) for node_id, demand, x, y in data]
depot_node = node_list[0]
customer_list = node_list[1:]
CAR_CAPACITY = 30

for start_node in node_list:
    for goal_node in node_list:
        x1, y1, x2, y2 = [start_node.x, start_node.y, goal_node.x, goal_node.y]
        start_node.distances[goal_node.node_id] = ((x1 - x2)**2 + (y1 - y2)**2)**0.5

class Chromosome:
    def __init__(self, node_list: List[Node] = None, path_list: List[List[Node]] = None) -> None:
        if node_list is None and path_list is None:
            raise ArgumentTypeError("Please specify either node_list or path_list.")
        elif node_list is not None and path_list is not None:
            raise ArgumentTypeError("Please specify only one among node_list and path_list.")
        
        if node_list is not None and path_list is None:
            node_permutation = np.random.permutation(node_list)
            self.path = []
            self.generate_entire_path(node_permutation)
        elif node_list is None and path_list is not None:
            self.path = path_list

        self.fitness = -1
        self.calculate_fitness() # overrides self.fitness

    def generate_entire_path(self, node_sequence):
        subpath = []
        subpath_storage = 0
        for n in node_sequence:
            if subpath_storage + n.demand <= CAR_CAPACITY:
                subpath.append(n)
                subpath_storage += n.demand
            else:
                self.path.append(Route(subpath, depot_node))
                subpath_storage = n.demand
                subpath = [n]
        self.path.append(Route(subpath, depot_node))
    
    def calculate_fitness(self):
        total_distance = sum([route.route_distance for route in self.path])
        self.fitness = 1/total_distance*1073 # normalize fitness (0, 1]

    def __mul__(self, other): # crossover operation
        path1 = deepcopy(self.path)
        path2 = deepcopy(other.path)
        subpath1 = np.random.choice(path1) # subpath is Route object
        subpath2 = np.random.choice(path2)

        # # DEBUGGING
        # print(subpath1, subpath2, "\n")

        child_path1 = self.BCRC_crossover(path1, subpath2.route)
        child_path2 = self.BCRC_crossover(path2, subpath1.route)

        child1 = Chromosome(path_list = child_path1)
        child2 = Chromosome(path_list = child_path2)

        return [child1, child2]
    
    def BCRC_crossover(self, original_path: List[Route], node_list: List[Node]):
        # deleting nodes in node_list from original_path list
        new_path = deepcopy(original_path)
        for n in node_list:
            for route in new_path:
                if n in route.route:
                    route.remove_node(n)
                    break
        
        # readding nodes in node_list to original_path_list
        for n in np.random.permutation(node_list):
            best_route_distance = float("inf")
            best_route_idx = None # int
            best_route = None # Route object
            for route_idx, route in enumerate(new_path):
                if route.storage_used + n.demand <= CAR_CAPACITY:
                    for i in range(route.length + 1):
                        new_route_list = route.route[0:i] + [n] + route.route[i:]
                        new_subroute = Route(new_route_list, depot_node)
                        if new_subroute.route_distance < best_route_distance:
                            best_route_distance = new_subroute.route_distance
                            best_route_idx = route_idx
                            best_route = new_subroute
            if best_route is None:
                new_path = new_path + Route([n], depot_node)
            else:
                new_path[best_route_idx] = best_route

        return new_path

    def mutation(self, beta: float):
        # for i in range(len(customer_list)):
        for i in range(7):
            if np.random.random() < beta:
                mutation_type = np.random.choice(["swap", 'shift', "invert"], p=[1, 0, 0])
                if mutation_type == "swap":
                    self.swap_mutation()
                elif mutation_type == "shift":
                    pass
                elif mutation_type == "invert":
                    pass
    
    def swap_mutation(self):
        x_route_idx = np.random.randint(len(self.path))
        x_node_idx = np.random.randint(len(self.path[x_route_idx].route))

        y_route_idx = np.random.randint(len(self.path))
        y_node_idx = np.random.randint(len(self.path[y_route_idx].route))

        # # DEBUGGING
        # print(x_route_idx, x_node_idx)
        # print(y_route_idx, y_node_idx, "\n")

        x_route = self.path[x_route_idx] # Route object
        y_route = self.path[y_route_idx]
        x_node = x_route.route[x_node_idx] # Node object
        y_node = y_route.route[y_node_idx]

        x_spaceleft = CAR_CAPACITY - (x_route.storage_used - x_node.demand)
        y_spaceleft = CAR_CAPACITY - (y_route.storage_used - y_node.demand)
        
        # Required conditions for swapping
        # 1. CAPACITY - (x_route.storage_used - x_node.demand) >= y_node.demand
        # 2. CAPACITY - (y_route.storage_used - y_node.demand) >= x_node.demand
        if x_spaceleft >= y_node.demand and y_spaceleft >= x_node.demand:
            self.path[x_route_idx].route[x_node_idx], self.path[y_route_idx].route[y_node_idx] = y_node, x_node
            self.path[x_route_idx].calculate_all()
            self.path[y_route_idx].calculate_all()
            self.calculate_fitness()

if __name__=="__main__":

    # # crossover testing
    # l = customer_list[:7]
    # print("nodes:", l, "\n")
    # p1 = Chromosome(l)
    # print("p1:", p1.path, p1.fitness, "\n")
    # p2 = Chromosome(l)
    # print("p1:", p2.path, p2.fitness, "\n")
    # c1, c2 = p1*p2
    # print("c1:", c1.path, c1.fitness, "\n")
    # print("c1:", c2.path, c2.fitness, "\n")

    # mutation testing
    l = customer_list[:7]
    print("nodes:", l, "\n")
    p = Chromosome(l)
    print("p:", p.path, p.fitness, "\n")
    p.mutation(0.1)
    print("p:", p.path, p.fitness, "\n")

    # # measuring initialization speed
    # start_time = time()
    # max_fitness = 0
    # min_fitness = 1
    # max_car = 0
    # for i in range(10000):
    #     c = Chromosome(customer_list)
    #     max_fitness = max(max_fitness, c.fitness)
    #     min_fitness = min(min_fitness, c.fitness)
    #     max_car = max(max_car, len(c.path))
    # print(time() - start_time)
    # print(max_fitness, min_fitness, max_car)

    pass