class Node:
    def __init__(self, node_id, demand, x, y):
        self.node_id: int = node_id
        self.demand: float = demand
        self.x: float = x
        self.y: float = y
        self.distances = {}  # dictionary {node_id: distance}

    def __eq__(self, other) -> bool:
        return self.node_id == other.node_id

    def __repr__(self) -> str:
        return str((self.node_id, self.demand, self.x, self.y))
