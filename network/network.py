import networkx as nx


class Network:
    def __init__(self):
        self.graph = nx.Graph()
        self.nodes: list[tuple[int, str, float]] = []
        self.edges: list[tuple[int, int, int, float]] = []

    def add_node(self, id: int, entity_title: str, sentiment: float):
        node = (id, entity_title, sentiment)
        self.nodes.append(node)
        self.graph.add_node(id, entity_title=entity_title, sentiment=sentiment)

    def add_edge(self, entity1: int, entity2: int, edge_thickness: int, edge_weight: float):
        edge = (entity1, entity2, edge_thickness, edge_weight)
        self.edges.append(edge)
        self.graph.add_edge(entity1, entity2, edge_thickness=edge_thickness, edge_weight=edge_weight)


"""
node: entity
node: color (total sentiment (green - to red)) 0-1 

edge: entity1, entity2, 
          edge_thickness: occurences, 
          edge_force: relatedness, (pull force)


EDGE_WEIGHT = EDGE_FORCE ... same thing 
"""
