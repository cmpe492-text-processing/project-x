from network import Network

if __name__ == "__main__":
    network = Network()

    network.add_node(1, "apple", 0.5)
    network.add_node(2, "banana", 0.7)
    network.add_node(3, "orange", 0.3)

    network.add_edge(1, 2, 5, 0.8)
    network.add_edge(1, 3, 3, 0.6)
    network.add_edge(2, 3, 2, 0.4)

    print(network.nodes)
