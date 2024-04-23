import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
from fetcher.src.tagme_manager import TagmeManager


def read_json_file(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


def process_data(data):
    results = {}
    for post in data:
        entities = post.get("entities", [])
        for entity in entities:
            wiki_id = entity["wiki_id"]
            if wiki_id in results.keys():
                # Update the sentiment and n if there is a sentiment
                if entity.get("sentiment", None) is None or results[wiki_id].get("sentiment", None) is None:
                    continue
                old_neutral = results[wiki_id]["sentiment"].get("neutral", 0)
                old_compound = results[wiki_id]["sentiment"].get("compound", 0)
                old_positive = results[wiki_id]["sentiment"].get("positive", 0)
                old_negative = results[wiki_id]["sentiment"].get("negative", 0)

                new_neutral = entity["sentiment"].get("neutral", 0)
                new_compound = entity["sentiment"].get("compound", 0)
                new_positive = entity["sentiment"].get("positive", 0)
                new_negative = entity["sentiment"].get("negative", 0)

                results[wiki_id]["sentiment"] = {
                    "neutral": old_neutral + new_neutral,
                    "compound": old_compound + new_compound,
                    "positive": old_positive + new_positive,
                    "negative": old_negative + new_negative,
                }

                results[wiki_id]["n"] += 1
            else:
                inserted_entity = {
                    "wiki_id": wiki_id,
                    "name": entity.get("name", ""),
                    "sentiment": entity.get("sentiment", {}),
                    "relatedness": entity.get("relatedness", None),
                    "n": 1
                }
                results[wiki_id] = inserted_entity
    return list(results.values())


def exporter(posts, center_entity_wiki_id, directory):
    direc = f'../../data/{directory}/'
    new_filename = f'{directory}_{center_entity_wiki_id}.json'
    with open(direc + new_filename, 'w') as f:
        json.dump(posts, f, indent=2)
        print(f'Exported {len(posts)} {directory} to {new_filename}')


def process_raw_data(center_entity_wiki_id, data):
    # Read the data from the file and create a new data that has center_entity as the center
    related_posts = []

    for post in data:
        entities = post.get("entities", [])
        for entity in entities:
            if "wiki_id" in entity and entity["wiki_id"] == center_entity_wiki_id:
                related_posts.append(post)
                break  # No need to check more entities if one matches

    return related_posts


def add_relatedness(posts, center_entity_wiki_id, tagme_manager):
    for post in posts:
        entities = post.get("entities", [])
        for entity in entities:
            if "wiki_id" in entity:
                relatedness = tagme_manager.relatedness_score(center_entity_wiki_id, entity["wiki_id"])
                print(f"Relatedness between {center_entity_wiki_id} and {entity['wiki_id']} is {relatedness}")
                entity["relatedness"] = relatedness
    return posts


def create_graph(data):
    """Creates and returns a graph from the entities list in JSON objects using a color gradient for sentiment."""
    import networkx as nx
    import matplotlib.colors as mcolors

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
        if not entity:
            continue

        node_name = entity.get("name", "Unknown")
        graph.add_node(node_name)
        labels[node_name] = node_name

        # Improved handling for 'None' or non-dictionary values
        sentiment_info = entity.get("sentiment", {})
        if sentiment_info is not None and isinstance(sentiment_info, dict):
            sentiment = sentiment_info.get("compound", 0)
        else:
            sentiment = 0

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
    # raw_data_filepath = "../../data/raw/corpus1.json"
    # raw_data = read_json_file(raw_data_filepath)
    # # Trump's wiki_id and label
    center_entity_wiki_id = 4848272
    text_label = 'Donald Trump'
    #
    # tagme_manager = TagmeManager(rho=0.1)
    #
    # if not isinstance(raw_data, list):
    #     raise ValueError("Expected a list of dictionaries in JSON file.")
    #
    # processed_data = process_raw_data(center_entity_wiki_id, raw_data)
    # result = add_relatedness(processed_data, center_entity_wiki_id, tagme_manager)
    #
    # exporter(result, center_entity_wiki_id, "processed")

    processed_data_filepath = f"../../data/processed/processed_{center_entity_wiki_id}.json"

    # Read the data from the file
    data = read_json_file(processed_data_filepath)

    # Ensure the data is a list
    if not isinstance(data, list):
        raise ValueError("Expected a list of dictionaries in JSON file.")
    # Process the data

    result = process_data(data)
    exporter(result, center_entity_wiki_id, "vision")

    vision_data_filepath = f"../../data/vision/vision_{center_entity_wiki_id}.json"

    data = read_json_file(vision_data_filepath)
    if not isinstance(data, list):
        raise ValueError("Expected a list of dictionaries in JSON file.")

    for fig_num, data_chunk in enumerate(chunk_data(data, 50)):
        graph, pos, labels, colors, sizes = create_graph(data_chunk)
        draw_graph(graph, pos, labels, colors, sizes, text_label, fig_num)


if __name__ == "__main__":
    main()
