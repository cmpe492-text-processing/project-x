import json

from fetcher.src.tagme_manager import TagmeManager


def read_json_file(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


def process_data(center_entity_wiki_id, data):
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


def exporter(posts, center_entity_wiki_id):
    processed_dir = '../../data/processed/'
    new_filename = f'corpus_{center_entity_wiki_id}.json'
    with open(processed_dir + new_filename, 'w') as f:
        json.dump(posts, f, indent=2)
        print(f'Exported {len(posts)} corpuses to {new_filename}')


def main():
    filepath = "../../data/raw/corpus1.json"

    # Read the data from the file
    data = read_json_file(filepath)

    # Ensure the data is a list
    if not isinstance(data, list):
        raise ValueError("Expected a list of dictionaries in JSON file.")

    # Process the data
    center_entity_wiki_id = 4848272
    result = process_data(center_entity_wiki_id, data)
    total_entities = 0
    for post in result:
        for entity in post.get("entities", []):
            if "wiki_id" in entity:
                total_entities += 1

    print(f"Found {total_entities} entities related to {center_entity_wiki_id}")

    tagme_manager = TagmeManager(rho=0.1)
    result = add_relatedness(result, center_entity_wiki_id, tagme_manager)

    exporter(result, center_entity_wiki_id)


if __name__ == "__main__":

    main()
