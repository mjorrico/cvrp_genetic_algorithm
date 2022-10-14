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
CAPACITY = 30

for start_node in node_list:
    for goal_node in node_list:
        x1, y1, x2, y2 = [start_node.x, start_node.y, goal_node.x, goal_node.y]
        start_node.distances[goal_node.node_id] = ((x1 - x2)**2 + (y1 - y2)**2)**0.5

class Chromosome:
    def __init__(self, node_list: List[Node] = []) -> None:
        self.sequence = np.random.permutation(node_list)
        self.path = []
        self.fitness = -1
        self.generate_entire_path() # overrides self.path
        self.calculate_fitness() # overrides self.fitness

    def generate_entire_path(self):
        if len(self.sequence) == 0:
            return 0
        subroute = []
        capacity_sum = 0
        for n in self.sequence:
            if capacity_sum + n.demand <= CAPACITY:
                subroute.append(n)
                capacity_sum += n.demand
            else:
                self.path.append(Route(subroute, capacity_sum, depot_node))
                capacity_sum = n.demand
                subroute = [n]
        self.path.append(Route(subroute, capacity_sum, depot_node))
    
    def calculate_fitness(self):
        if len(self.path) == 0:
            return 0
        total_distance = sum([route.route_distance for route in self.path])
        self.fitness = 1/total_distance*1073 # normalize fitness (0, 1]

    def __mul__(self, other): # crossover operation
        path1 = self.path
        path2 = other.path
        subroute1 = np.random.choice(path1)
        subroute2 = np.random.choice(path2)

        print(subroute1)
        print(subroute2)
        print()

        path1 = self._delete_crossover(path1, subroute2.route) # List[Route], List[Node]
        self.calculate_fitness()
        path2 = self._delete_crossover(path2, subroute1.route)
        other.calculate_fitness()

        path1 = self._input_crossover(path1, subroute2.route)
        path2 = self._input_crossover(path2, subroute1.route)

        child1 = Chromosome([])
        child2 = Chromosome([])
        child1.path = path1
        child2.path = path2
        child1.calculate_fitness()
        child2.calculate_fitness()

        return [child1, child2]
    
    def _delete_crossover(self, route_list: List[Route], node_delete_list: List[Node]):
        for n in node_delete_list:
            for subroute in route_list:
                if n in subroute.route:
                    subroute.route.remove(n)
                    subroute.required_capacity -= n.demand
                    subroute.calculate_distance()
                    break
        return route_list

    def _input_crossover(self, route_list: List[Route], node_insert_list: List[Node]):
        for n in np.random.permutation(node_insert_list):
            best_route_in_path_distance = float("inf")
            best_route_in_path_idx = None # int
            best_route_in_path = None # Route object
            for subroute_idx, subroute in enumerate(route_list):
                if subroute.required_capacity + n.demand <= CAPACITY:
                    for idx in range(len(subroute.route) + 1):
                        new_route_list = subroute.route[0:idx] + [n] + subroute.route[idx:]
                        new_required_capacity = subroute.required_capacity + n.demand
                        new_subroute = Route(new_route_list, new_required_capacity, depot_node)
                        if new_subroute.route_distance < best_route_in_path_distance:
                            best_route_in_path_distance = new_subroute.route_distance
                            best_route_in_path_idx = subroute_idx
                            best_route_in_path = new_subroute
            if best_route_in_path is None:
                route_list = route_list + Route([n],n.demand, depot_node)
            else:
                route_list[best_route_in_path_idx] = best_route_in_path
        return route_list

    def mutation(self, beta: float):
        for i in range(len(customer_list)):
            if np.random.random() < beta:
                mutation_type = np.random.choice([0, 1, 2], p=[1, 0, 0])
                if mutation_type == 0: # SWAP
                    x_route_idx = np.random.randint(len(self.path))
                    x_node_idx = np.random.randint(len(self.path[x_route_idx].route))

                    y_route_idx = np.random.randint(len(self.path))
                    y_node_idx = np.random.randint(len(self.path[y_route_idx].route))

                    x_route = self.path[x_route_idx]
                    y_route = self.path[y_route_idx]
                    x_node = self.path[x_route_idx].route[x_node_idx]
                    y_node = self.path[y_route_idx].route[y_node_idx]

                    x_spaceleft = CAPACITY - (x_route.required_capacity - x_node.demand)
                    y_spaceleft = CAPACITY - (y_route.required_capacity - y_node.demand)
                    
                    # Required conditions for swapping
                    # 1. CAPACITY - (route_x.required_capacity - node_x.demand) >= node_y.demand
                    # 2. CAPACITY - (route_y.required_capacity - node_y.demand) >= node_x.demand
                    if x_spaceleft >= y_node.demand and y_spaceleft >= x_node.demand:
                        self.path[x_route_idx].route[x_node_idx], self.path[y_route_idx].route[y_node_idx] = y_node, x_node
                        
                    print(x_node, y_node)
                    break

                elif mutation_type == 1: # SHIFT
                    pass
                else: # INVERT
                    pass




# TODO: CHECK CODES ABOVE IF ROUTE CHANGES BUT ROUTE.ROUTE_DISTANCE AND SELF.FITNESS ISN'T UPDATED
# CALL Route.calculate_distance() before calling Chromosome.calculate_fitness()


if __name__=="__main__":
    pass
    l = customer_list[:5]
    print(l)
    print()
    p1 = Chromosome(l)
    print(p1.path, p1.fitness)
    print()
    # p2 = Chromosome(l)
    # print(p2.path, p2.fitness)
    # print()
    # c1, c2 = p1*p2
    # print(c1.path, c1.fitness)
    # print()
    # print(c2.path, c2.fitness)
    # print()
    

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