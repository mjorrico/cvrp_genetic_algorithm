from copy import deepcopy
from functools import cached_property
from node import Node
from route import Route

from typing import List

import matplotlib.pyplot as plt
import numpy as np


class Chromosome:
    def __init__(
        self, input_list: List[Route], car_capacity: float, depot_node: Node
    ):
        self.path = input_list
        self.car_capacity = car_capacity
        self.depot_node = depot_node
        self._initialize_attributes()

    @cached_property
    def distance(self):
        return sum([route.route_distance for route in self.path])

    @cached_property
    def fitness(self):
        return 1 / self.distance * 1073  # normalize fitness (0, 1]

    @classmethod
    def from_node_list(
        cls, customer_list: List[Node], car_capacity: float, depot_node: Node
    ):
        node_sequence = np.random.permutation(customer_list)
        path = []
        subpath = []
        subpath_storage = 0
        for n in node_sequence:
            if subpath_storage + n.demand <= car_capacity:
                subpath.append(n)
                subpath_storage += n.demand
            else:
                path.append(Route(subpath, depot_node))
                subpath_storage = n.demand
                subpath = [n]
        path.append(Route(subpath, depot_node))
        return Chromosome(path, car_capacity, depot_node)

    def __mul__(self, other):  # crossover operation
        path1: List[Route] = deepcopy(self.path)
        path2: List[Route] = deepcopy(other.path)
        subpath1: Route = np.random.choice(path1)
        subpath2: Route = np.random.choice(path2)

        child_path1 = self.BCRC_crossover(path1, subpath2.route)
        child_path2 = self.BCRC_crossover(path2, subpath1.route)

        child1 = Chromosome(child_path1, self.car_capacity, self.depot_node)
        child2 = Chromosome(child_path2, self.car_capacity, self.depot_node)

        return [child1, child2]

    def BCRC_crossover(
        self, path: List[Route], node_list: List[Node]
    ) -> List[Route]:
        # deleting nodes in node_list from path list
        for n in node_list:
            for route in path:
                if n in route.route:
                    route.remove_node(n)
                    break

        # removing empty routes
        path = [r for r in path if r.length > 0]

        # re-adding nodes in node_list to original_path_list
        for n in np.random.permutation(node_list):
            best_route_distance_improvement = float("inf")
            best_route_idx: int = None
            best_route: Route = None
            for route_idx, route in enumerate(path):
                if route.storage_used + n.demand <= self.car_capacity:
                    for i in range(route.length + 1):
                        new_route = Route(
                            route.route[0:i] + [n] + route.route[i:],
                            self.depot_node,
                        )  # This can be more efficient. Do not create new Route object to calculate new path length
                        distance_gain = (
                            new_route.route_distance - route.route_distance
                        )
                        if distance_gain < best_route_distance_improvement:
                            best_route_distance_improvement = distance_gain
                            best_route_idx = route_idx
                            best_route = new_route
            if best_route is None:
                path.append(Route([n], self.depot_node))
            else:
                path[best_route_idx] = best_route

        return path

    def mutation(self, beta: float):
        if np.random.random() < beta:
            x_route_idx = np.random.randint(len(self.path))
            x_node_idx = np.random.randint(len(self.path[x_route_idx].route))

            y_route_idx = np.random.randint(len(self.path))
            y_node_idx = np.random.randint(len(self.path[y_route_idx].route))

            x_route = self.path[x_route_idx]
            y_route = self.path[y_route_idx]
            x_node = x_route.route[x_node_idx]
            y_node = y_route.route[y_node_idx]

            x_spaceleft = self.car_capacity - (
                x_route.storage_used - x_node.demand
            )
            y_spaceleft = self.car_capacity - (
                y_route.storage_used - y_node.demand
            )

            if x_spaceleft >= y_node.demand and y_spaceleft >= x_node.demand:
                (
                    self.path[x_route_idx].route[x_node_idx],
                    self.path[y_route_idx].route[y_node_idx],
                ) = (y_node, x_node)
                self.path[x_route_idx]._recompute_route()
                self.path[y_route_idx]._recompute_route()
                self._recompute_chromosome()

    def _recompute_chromosome(self):
        del self.distance, self.fitness
        self._initialize_attributes()

    def _initialize_attributes(self):
        _ = self.distance
        _ = self.fitness  # recomputes distance and fitness

    def __gt__(self, other):
        if isinstance(self, Chromosome) and isinstance(other, Chromosome):
            return self.fitness > other.fitness
        else:
            raise TypeError

    def __str__(self):
        general_info = [
            f"Number of routes: {len(self.path)}\nDistance: {self.distance}"
        ]
        path_info = [
            f"Route {i+1} -> {r.route} (Distance: {r.route_distance})"
            for i, r in enumerate(self.path)
        ]
        return "\n".join(general_info + path_info)

    def save_figure(self, filename="chromosome.jpg"):
        legend = ["Car " + str(i + 1) for i in range(len(self.path))]
        x_depot = self.depot_node.x
        y_depot = self.depot_node.y
        for route in self.path:
            x = [x_depot] + [node.x for node in route.route] + [x_depot]
            y = [y_depot] + [node.y for node in route.route] + [y_depot]
            plt.plot(x, y, marker="o")
        plt.legend(legend)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title("Paths Taken By Each Delivery Cars")
        plt.xlim([-2.5, 130])
        plt.savefig(filename, dpi=600)
        print('Image saved as "{}".'.format(filename))
