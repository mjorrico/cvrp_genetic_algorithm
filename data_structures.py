from typing import List

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
        return str((self.demand, self.x, self.y))
        # return str(self.demand)
        # return "Node(" + str(self.node_id) + ", " + str(self.demand) + ", " + str(self.x) + ", " + str(self.y) + ")"

class Route:
    def __init__(self, route_list: List[Node], depot_node: Node):
        self.route = route_list
        self.depot_node = depot_node
        self.route_distance = -1
        self.storage_used = -1
        self.length = -1
        self.calculate_all()
    
    def calculate_all(self):
        self.calculate_distance()
        self.calculate_storage()
        self.calculate_length()

    def calculate_distance(self):
        route = [self.depot_node] + self.route + [self.depot_node]
        route_distance = 0
        for i in range(len(route) - 1):
            start_node = route[i]
            goal_node_id = route[i+1].node_id
            route_distance += start_node.distances[goal_node_id]
        self.route_distance = route_distance
    
    def calculate_storage(self):
        self.storage_used = sum([n.demand for n in self.route])

    def calculate_length(self):
        self.length = len(self.route)

    def remove_node(self, node: Node):
        if node in self.route:
            self.route.remove(node)
            self.calculate_all()

    def __repr__(self):
        return str(self.route)