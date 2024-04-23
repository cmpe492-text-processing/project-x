import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os


def read_json_file(filepath):
    """Reads a JSON file and returns the data."""
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


def create_graph(data):
    """Creates and returns a graph from the entities list in JSON objects using a color gradient for sentiment."""
    graph = nx.Graph()
    labels = {}
    node_colors = []
    node_sizes = []

    cmap = mcolors.LinearSegmentedColormap.from_list(
        name='sentiment_color',
        colors=['red', 'grey', 'green']
    )

    norm = mcolors.Normalize(vmin=-1, vmax=1)

    for entity in data:
        node_name = entity["name"]
        graph.add_node(node_name)
        labels[node_name] = node_name

        sentiment = entity["sentiment"]["compound"]
        color = cmap(norm(sentiment))
        node_colors.append(color)

        node_sizes.append(entity.get("relatedness", 0.1) * 2000 + 50)

    pos = nx.spring_layout(graph)
    return graph, pos, labels, node_colors, node_sizes


def draw_graph(graph, pos, labels, node_colors, node_sizes, text_label, fig_num):
    plt.figure(figsize=(15, 10))
    nx.draw(
        graph,
        pos,
        labels=labels,
        with_labels=True,
        node_color=node_colors,
        node_size=node_sizes,
        font_size=8,
        font_weight="bold",
        edge_color="grey",
        alpha=0.7
    )

    center_x = sum(x for x, y in pos.values()) / len(pos)
    center_y = sum(y for x, y in pos.values()) / len(pos)
    plt.text(center_x, center_y, text_label, fontsize=18, color='black', horizontalalignment='center', verticalalignment='center')

    output_dir = f'./graphs/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filepath = os.path.join(output_dir, f'{text_label}_{fig_num}.png')
    plt.savefig(filepath, format="PNG", dpi=300)
    plt.show()


def chunk_data(data, chunk_size):
    """Generator to divide data into chunks."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def main():
    center_entity_wiki_id = 4848272
    filepath = f"../../data/vision/vision_{center_entity_wiki_id}.json"

    data = read_json_file(filepath)
    if not isinstance(data, list):
        raise ValueError("Expected a list of dictionaries in JSON file.")

    text_label = 'Donald Trump'
    for fig_num, data_chunk in enumerate(chunk_data(data, 50)):
        graph, pos, labels, colors, sizes = create_graph(data_chunk)
        draw_graph(graph, pos, labels, colors, sizes, text_label, fig_num)


if __name__ == "__main__":
    main()
