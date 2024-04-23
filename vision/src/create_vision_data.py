import json

from sympy.parsing.sympy_parser import null


def read_json_file(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


def process_data(center_entity_wiki_id, data):
    results = {}

    for post in data:
        entities = post.get("entities", [])
        for entity in entities:
            wiki_id = entity["wiki_id"]
            if wiki_id in results.keys():
                # Update the sentiment and n if there is a sentiment
                if entity.get("sentiment", null) is None or results[wiki_id].get("sentiment", null) is None:
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
                # Store initial sentiment directly
                inserted_entity = {
                    "wiki_id": wiki_id,
                    "name": entity.get("name", ""),
                    "sentiment": entity.get("sentiment", {}),
                    "relatedness": entity.get("relatedness", null),
                    "n": 1
                }
                results[wiki_id] = inserted_entity
    return list(results.values())


def exporter(posts, center_entity_wiki_id):
    vision_dir = '../../data/vision/'
    new_filename = f'vision_{center_entity_wiki_id}.json'
    with open(vision_dir + new_filename, 'w') as f:
        json.dump(posts, f, indent=2)
        print(f'Exported {len(posts)} vision to {new_filename}')


def main():
    center_entity_wiki_id = 4848272
    filepath = f"../../data/processed/corpus_{center_entity_wiki_id}.json"

    # Read the data from the file
    data = read_json_file(filepath)

    # Ensure the data is a list
    if not isinstance(data, list):
        raise ValueError("Expected a list of dictionaries in JSON file.")
    # Process the data

    result = process_data(center_entity_wiki_id, data)
    exporter(result, center_entity_wiki_id)


if __name__ == "__main__":
    main()
