class Graph:
    def __init__(self):
        self.nodes = {}     # Dictionary for nodes
        self.edges = {}     # Dictionary for edges
    
    def add_node(self, node_id, data):
        if node_id not in self.nodes:
            self.nodes[node_id] = data
            self.edges[node_id] = []
    
    def add_edge(self, node_id1, node_id2, weight=None):
        """can optionally add weight to edge"""
        if node_id1 in self.nodes and node_id2 in self.nodes:
            self.edges[node_id1].append((node_id2, weight))
            self.edges[node_id2].append((node_id1, weight))
    
    def get_neighbors(self, node_id):
        return self.edges.get(node_id, [])
    
    def get_node_data(self, node_id):
        return self.nodes.get(node_id)