from node import Node
import csv
import numpy as np


class CVRPProblem:
    def __init__(self, filepath: str, car_capacity: float) -> None:
        self._filepath = filepath
        self.car_capacity = car_capacity

    @property
    def _node_list(self):
        with open(self._filepath, newline="") as r:
            reader = csv.reader(r, delimiter=";")
            data = np.array(list(reader)[1:], dtype=np.int64)

        temp_node_list = [
            Node(node_id, demand, x, y) for node_id, demand, x, y in data
        ]

        for start_node in temp_node_list:
            for goal_node in temp_node_list:
                x1, y1, x2, y2 = [
                    start_node.x,
                    start_node.y,
                    goal_node.x,
                    goal_node.y,
                ]
                start_node.distances[goal_node.node_id] = (
                    (x1 - x2) ** 2 + (y1 - y2) ** 2
                ) ** 0.5

        return temp_node_list

    @property
    def depot_node(self):
        for n in self._node_list:
            if n.demand == 0:
                return n
        raise RuntimeError(
            "Depot can't be found. Make sure there is a node with demand 0"
        )

    @property
    def customer_list(self):
        result = self._node_list
        result.remove(self.depot_node)
        return result

    @property
    def n_customers(self):
        return len(self.customer_list)
