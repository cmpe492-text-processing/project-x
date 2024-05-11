import json
from corpus_generator.src.tagme_manager import TagmeManager
from time import gmtime, strftime

class FeatureExtractor:
    def __init__(self, wiki_id):
        self.wiki_id = wiki_id
        self.db_dump_filepath = "../../data/db_dumps/db_dump.json"

    @staticmethod
    def read_json_file(filepath):
        with open(filepath, "r") as file:
            data = json.load(file)
        return data

    @staticmethod
    def exporter(posts, center_entity_wiki_id, directory):
        direc = f'../../data/{directory}/'
        new_filename = f'{directory}_{center_entity_wiki_id}.json'
        with open(direc + new_filename, 'w') as f:
            json.dump(posts, f, indent=2)
            print(f'Exported {len(posts)} {directory} to {new_filename}')

    @staticmethod
    def get_related_corpuses(center_entity_wiki_id, data):
        related_corpuses = []
        for post in data:
            entities = post.get("entities", [])
            for entity in entities:
                if "wiki_id" in entity and entity["wiki_id"] == center_entity_wiki_id:
                    related_corpuses.append(post)
                    break
        return related_corpuses

    @staticmethod
    def add_relatedness(posts, center_entity_wiki_id, tagme_manager):
        # Load existing relatedness scores from the file into a dictionary for faster lookups
        relatedness_dict = {}
        with open("../../data/relatedness_scores.txt", "r") as file:
            for line in file:
                entity_1, entity_2, relatedness = line.strip().split('\t')
                relatedness_dict[(entity_1, entity_2)] = float(relatedness)

        # Process each post to update or compute relatedness
        for post in posts:
            entities = post.get("entities", [])
            for entity in entities:
                wiki_id = entity.get("wiki_id")
                if wiki_id:
                    key = (center_entity_wiki_id, wiki_id)
                    reverse_key = (wiki_id, center_entity_wiki_id)

                    # Check if relatedness already exists
                    if key in relatedness_dict:
                        entity["relatedness"] = relatedness_dict[key]
                    elif reverse_key in relatedness_dict:
                        entity["relatedness"] = relatedness_dict[reverse_key]
                    else:
                        # Compute relatedness and update the dictionary
                        relatedness_score = tagme_manager.relatedness_score(center_entity_wiki_id, wiki_id)
                        entity["relatedness"] = relatedness_score
                        relatedness_dict[key] = relatedness_score
                        # Append new relatedness score to the file
                        with open("../../data/relatedness_scores.txt", "a") as append_file:
                            append_file.write(f"{center_entity_wiki_id}\t{wiki_id}\t{relatedness_score}\n")

        return posts

    def create_extracted_features_json(self):
        raw_data = self.read_json_file(self.db_dump_filepath)
        print('read raw data', strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        tagme_manager = TagmeManager(rho=0.1)

        if not isinstance(raw_data, list):
            raise ValueError("Expected a list of dictionaries in JSON file.")

        related_corpuses_without_relatedness = self.get_related_corpuses(self.wiki_id, raw_data)
        print('got the corpuses', strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        related_corpuses = self.add_relatedness(related_corpuses_without_relatedness, self.wiki_id, tagme_manager)
        print('added the relatedness', strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        data = related_corpuses

        result = self.process_data(data)
        print('processed the data', strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        self.exporter(result, self.wiki_id, "feature_extracted_data")

        return result

    @staticmethod
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


def main():
    feature_extractor = FeatureExtractor(4848272)
    feature_extractor.create_extracted_features_json()


if __name__ == "__main__":
    main()
