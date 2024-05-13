from network import Network

if __name__ == "__main__":
    network = Network()

    network.add_node(1, "apple", 0.5)
    network.add_node(2, "banana", 0.7)
    network.add_node(3, "orange", 0.3)
    network.add_node(4, "cabbage", 0.9)
    network.add_node(5, "carrot", 0.1)
    network.add_node(6, "potato", 0.6)

    network.add_edge(1, 2, 5, 0.8)
    network.add_edge(1, 3, 3, 0.6)
    network.add_edge(2, 3, 2, 0.4)
    network.add_edge(4, 5, 1, 0.2)
    network.add_edge(5, 6, 4, 0.7)
    network.add_edge(6, 4, 6, 0.9)
    network.add_edge(1, 6, 2, 0.5)

    print(network.degree_centrality())
    print(network.communities())
    print(network.shortest_path(1, 4))

    network.draw()
