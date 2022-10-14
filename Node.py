class Node:
    def __init__(self, node_id, demand, x, y):
        self.node_id = node_id
        self.demand = demand
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.node_id == other.node_id
    
    def __repr__(self) -> str:
        return str(self.demand)
        # return "Node(" + str(self.node_id) + ", " + str(self.demand) + ", " + str(self.x) + ", " + str(self.y) + ")"