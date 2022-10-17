from typing import List
from time import time
from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
import functools
import csv

class Node:
    def __init__(self, node_id, demand, x, y):
        self.node_id = node_id
        self.demand = demand
        self.x = x
        self.y = y
        self.distances = {} # {node_id: distance}

    def __eq__(self, other):
        return self.node_id == other.node_id
    
    def __repr__(self) -> str:
        return str((self.node_id, self.demand, self.x, self.y))

with open("data.csv", newline='') as r:
    reader = csv.reader(r, delimiter=";")
    data = np.array(list(reader)[1:], dtype = np.int64)

node_list = [Node(node_id, demand, x, y) for node_id, demand, x, y in data]

for start_node in node_list:
    for goal_node in node_list:
        x1, y1, x2, y2 = [start_node.x, start_node.y, goal_node.x, goal_node.y]
        start_node.distances[goal_node.node_id] = ((x1 - x2)**2 + (y1 - y2)**2)**0.5

depot_node = node_list[0]
customer_list = node_list[1:]
CAR_CAPACITY = 100

class Route:
    def __init__(self, route_list: List[Node], depot_node: Node):
        self.route = route_list
        self.depot_node = depot_node

    @property
    def route_distance(self) -> float:
        real_route = [self.depot_node] + self.route + [self.depot_node]
        distance = 0
        for i in range(len(real_route) - 1):
            start_node = real_route[i]
            goal_node_id = real_route[i+1].node_id
            distance += start_node.distances[goal_node_id]
        return distance
    
    @property
    def storage_used(self):
        return sum([n.demand for n in self.route])

    @property
    def length(self):
        return len(self.route)

    def remove_node(self, node: Node):
        if node in self.route:
            self.route.remove(node)

    def __repr__(self):
        return "Route: " + str(self.route) + "\n" + "Distance: " + str(self.route_distance)

class Chromosome:
    def __init__(self, input_list: List[Route]) -> None:
        if not isinstance(input_list, List) or len(input_list) < 1 or not isinstance(input_list[0], Route):
            raise TypeError
        else:
            self.path = input_list

    @property
    def distance(self):
        return sum([route.route_distance for route in self.path])

    @property
    def fitness(self):
        return 1/self.distance*1073 # normalize fitness (0, 1]

    @classmethod
    def from_node_list(cls, node_sequence: List[Node]):
        node_sequence = np.random.permutation(node_sequence)
        path = []
        subpath = []
        subpath_storage = 0
        for n in node_sequence:
            if subpath_storage + n.demand <= CAR_CAPACITY:
                subpath.append(n)
                subpath_storage += n.demand
            else:
                path.append(Route(subpath, depot_node))
                subpath_storage = n.demand
                subpath = [n]
        path.append(Route(subpath, depot_node))
        return cls(path)

    def __mul__(self, other): # crossover operation
        path1 = deepcopy(self.path)
        path2 = deepcopy(other.path)
        subpath1 = np.random.choice(path1) # subpath is Route object
        subpath2 = np.random.choice(path2)

        child_path1 = self.BCRC_crossover(path1, subpath2.route)
        child_path2 = self.BCRC_crossover(path2, subpath1.route)

        child1 = Chromosome(child_path1)
        child2 = Chromosome(child_path2)

        return [child1, child2]
    
    def BCRC_crossover(self, original_path: List[Route], node_list: List[Node]):
        # deleting nodes in node_list from original_path list
        new_path = deepcopy(original_path)
        for n in node_list:
            for route in new_path:
                if n in route.route:
                    route.remove_node(n)
                    break
        
        # removing empty routes
        new_path = [r for r in new_path if r.length > 0]
        
        # re-adding nodes in node_list to original_path_list
        for n in np.random.permutation(node_list):
            best_route_distance_improvement = float("inf")
            best_route_idx = None # int
            best_route = None # Route object
            for route_idx, route in enumerate(new_path):
                if route.storage_used + n.demand <= CAR_CAPACITY:
                    for i in range(route.length + 1):
                        new_route_list = route.route[0:i] + [n] + route.route[i:]
                        new_route = Route(new_route_list, depot_node)
                        if new_route.route_distance - route.route_distance < best_route_distance_improvement:
                            best_route_distance_improvement = new_route.route_distance - route.route_distance
                            best_route_idx = route_idx
                            best_route = new_route
            if best_route is None:
                new_path = new_path + [Route([n], depot_node)]
            else:
                new_path[best_route_idx] = best_route

        return new_path

    def mutation(self, beta: float):
        for i in range(len(customer_list)):
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

    def __gt__(self, other):
        if isinstance(self, Chromosome) and isinstance(other, Chromosome):
            return self.fitness > other.fitness
        else:
            raise TypeError
    
    def __str__(self):
        general_info = ["Number of routes: {}\nDistance: {}".format(len(self.path), self.distance)]
        path_info = ["Route {} -> {} (Distance: {})".format(i+1, r.route, r.route_distance) for i, r in enumerate(self.path)]
        return "\n".join(general_info+path_info)

    def save_figure(self, filename = "chromosome.jpg"):
        legend = ["Car " + str(i+1) for i in range(len(self.path))]
        x_depot = depot_node.x
        y_depot = depot_node.y
        for route in self.path:
            x = [x_depot] + [node.x for node in route.route] + [x_depot]
            y = [y_depot] + [node.y for node in route.route] + [y_depot]
            plt.plot(x, y, marker = "o")
        plt.legend(legend)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title("Paths Taken By Each Delivery Cars")
        plt.xlim([-2.5, 130])
        plt.savefig(filename, dpi=600)
        print("Image saved as \"{}\".".format(filename))

def generate_population(n_population: int = 10):
    return sorted([Chromosome.from_node_list(customer_list) for i in range(n_population)])

def select_parents(chr_list: List[Chromosome]):
    fitness_list = [c.fitness for c in chr_list]
    sum_fitness = sum(fitness_list)
    roulette_rank = [f/sum_fitness for f in fitness_list]
    return np.random.choice(chr_list, 2, False, roulette_rank)

def withtime(f):
    @functools.wraps(f)
    def f_withtime(*args, **kwargs):
        print("Running!")
        start_time = time()
        f_result = f(*args, **kwargs)
        end_time = time()
        print("Wall time: {} seconds".format(str(end_time - start_time)))
        return f_result
    return f_withtime