import networkx as nx

def create_network():
    G = nx.Graph()

    # Add nodes (routers)
    G.add_nodes_from([1, 2, 3, 4, 5, 6])

    # Add edges (connections) with capacity (max bandwidth)
    G.add_edge(1, 2, capacity=100)
    G.add_edge(1, 3, capacity=100)
    G.add_edge(2, 4, capacity=80)
    G.add_edge(3, 4, capacity=80)
    G.add_edge(4, 5, capacity=60)
    G.add_edge(4, 6, capacity=60)
    G.add_edge(5, 6, capacity=100)

    return G


if __name__ == '__main__':
    network = create_network()
    print("Nodes:", list(network.nodes()))
    print("Edges:", list(network.edges()))
    print("Network created successfully!")