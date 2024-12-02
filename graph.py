class Graph:
    def __init__(self):
        self.nodes = {}  # Dictionary for nodes
        self.edges = {}  # Dictionary for edges

    def add_node(self, node_id, data):
        if node_id not in self.nodes:
            self.nodes[node_id] = data
            self.edges[node_id] = []

    def add_edge(self, node_id1, node_id2, weight=None):
        """Can optionally add weight to edge"""
        if node_id1 in self.nodes and node_id2 in self.nodes:
            self.edges[node_id1].append((node_id2, weight))
            self.edges[node_id2].append((node_id1, weight))

    def get_neighbors(self, node_id):
        return self.edges.get(node_id, [])

    def get_node_data(self, node_id):
        return self.nodes.get(node_id)

    def add_data_with_relationships(self, data, relationships):
     
        # Add nodes
        for node_id, node_data in data.items():
            self.add_node(node_id, node_data)

        # Add edges
        for relationship in relationships:
            if len(relationship) == 3:
                node_id1, node_id2, weight = relationship
                self.add_edge(node_id1, node_id2, weight)
            elif len(relationship) == 2:
                node_id1, node_id2 = relationship
                self.add_edge(node_id1, node_id2)
