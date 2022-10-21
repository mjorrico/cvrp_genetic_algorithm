from node import Node
from functools import cached_property
from typing import List


class Route:
    def __init__(self, route_list: List[Node], depot_node: Node):
        self.route = route_list
        self.depot_node = depot_node
        self._initialize_attributes()

    @cached_property
    def route_distance(self) -> float:
        real_route = [self.depot_node] + self.route + [self.depot_node]
        distance = 0
        for i in range(len(real_route) - 1):
            start_node = real_route[i]
            goal_node_id = real_route[i + 1].node_id
            distance += start_node.distances[goal_node_id]
        return distance

    @cached_property
    def storage_used(self):
        used = int(
            0 if len(self.route) == 0 else sum([n.demand for n in self.route])
        )
        return used

    @cached_property
    def length(self):
        return len(self.route)

    def remove_node(self, node: Node):
        self.route.remove(node)
        self._recompute_route()

    def _recompute_route(self):
        # try:
        del self.route_distance
        del self.storage_used
        del self.length
        self._initialize_attributes()  # updating attributes after self.route changes

    def _initialize_attributes(self):
        _ = self.route_distance
        _ = self.storage_used
        _ = self.length  # caching distance storage and length

    def __repr__(self):
        return (
            "Route: "
            + str(self.route)
            + "\n"
            + "Distance: "
            + str(self.route_distance)
        )
