import enum

from tagme import Annotation
from fetcher.src import reddit as rddt
import database as db
from fetcher.src.processor import TextProcessor
from fetcher.src.tagme_manager import TagmeManager
import json
import re

DEBUG = True


class Platform(enum.Enum):
    REDDIT = "reddit"
    TWITTER = "twitter"

    def __str__(self):
        return self.value


"""
    list[Corpuses]
    [
        {
            platform: "reddit/politics",
            id: "123",
            title: "title",
            body: "body",
            sentiment: 0.5, # -1 to 1
            entities: [
                {
                    name: "entity1",
                    location: "title",
                    begin: 0,
                    end: 5,
                    sentiment: 0.5,
                    wiki_id: "Q123",
                    wiki_info: {
                        P31: ["Q5"],
                        P21: ["Q123"],
                        P17: ["Q456"]
                    }, 
                    dependent_entities: [
                        {
                            name: "entity2",
                            relatedness: 0.5
                            sentiment: 0.5
                        }, 
                        {
                            name: "entity3",
                            relatedness: 0.5
                            sentiment: 0.5
                        }
                    ]
                }, 
                {
                    name: "entity2",
                    location: "body",
                    begin: 10,
                    end: 20,
                    sentiment: 0.5,
                    related_entities: [
                        {
                            name: "entity1",
                            relatedness: 0.5
                            sentiment: 0.5
                        }, 
                        {
                            name: "entity3",
                            relatedness: 0.5
                            sentiment: 0.5
                        }
                    ]
                }
            ]  
        },
        {

        }
        .
        .
        .
        {

        }
    ]

"""


def preprocess_text(text):
    # Replace common escape sequences with their actual character representations
    # You might need to add more replacements based on the escape sequences you encounter
    replacements = {
        '\\n': '\n',  # Newline
        '\\t': '\t',  # Tab
        '\\\\': '\\'  # Backslash
    }
    for escaped, char in replacements.items():
        text = text.replace(escaped, char)
    return text


def find_closest_match(original_text, mention, start_index):
    pattern = re.escape(mention)
    for match in re.finditer(pattern, original_text, re.IGNORECASE):
        if abs(match.start() - start_index) <= len(mention):
            return match.start(), match.end()
    return None, None


def adjust_entity_indices(original_text, cleaned_text, entity):
    # Preprocess the original text to handle escaped characters
    preprocessed_original_text = preprocess_text(original_text)

    cleaned_begin = entity['begin']
    cleaned_end = entity['end']
    mention = entity['mention']

    # Estimate the original start index (a simple heuristic)
    original_index = preprocessed_original_text.find(mention, cleaned_begin - 5 if cleaned_begin > 5 else 0)

    if original_index != -1:
        entity['begin'] = original_index
        entity['end'] = original_index + len(mention)
    else:
        # If not found with the simple heuristic, use a more robust method
        original_begin, original_end = find_closest_match(preprocessed_original_text, mention, cleaned_begin)
        if original_begin is not None and original_end is not None:
            entity['begin'] = original_begin
            entity['end'] = original_end
    return entity


def generate_corpus(platform: Platform,
                    platform_ext: str,
                    platform_id: str,
                    title: str,
                    body: str) -> dict:

    corpus: dict = {"platform": platform.value + "/" + platform_ext if platform_ext else platform.value,
                    "id": platform_id,
                    "title": title,
                    "body": body}

    # clean text - remove special characters, remove stopwords, lower case, etc
    text_processor = TextProcessor()
    cleaned_title = text_processor.clean_text(title)
    cleaned_body = text_processor.clean_text(body)

    # NER (Named Entity Recognition) - tag entities in text
    tagme_manager = TagmeManager(rho=0.15)
    tagged_title: list[Annotation] = tagme_manager.tag_text(cleaned_title)
    tagged_body: list[Annotation] = tagme_manager.tag_text(cleaned_body)

    if DEBUG:
        print("Title:")
        print(cleaned_title)
        print("Body:")
        print(cleaned_body)

    # create entities with their base tagme information
    entities = []
    for annotation in tagged_title:
        entity = {
            "name": annotation.entity_title,
            "location": "title",
            "mention": annotation.mention,
            "begin": annotation.begin,
            "end": annotation.end,
            "confidence": annotation.score,
            "sentiment": None,
            "wiki_id": annotation.entity_id,
            "wiki_info": {},
            "dependent_entities": []
        }
        adjusted_entity = adjust_entity_indices(title, cleaned_title, entity)
        entities.append(adjusted_entity)

    for annotation in tagged_body:
        entity = {
            "name": annotation.entity_title,
            "location": "body",
            "mention": annotation.mention,
            "begin": annotation.begin,
            "end": annotation.end,
            "confidence": annotation.score,
            "sentiment": None,
            "wiki_id": annotation.entity_id,
            "wiki_info": {},
            "dependent_entities": []
        }
        adjusted_entity = adjust_entity_indices(body, cleaned_body, entity)
        entities.append(adjusted_entity)

    # filter entities that have their indices adjusted
    for entity in entities:
        if entity['location'] == 'title':
            found_word = title[entity['begin']:entity['end']]
        elif entity['location'] == 'body':
            found_word = body[entity['begin']:entity['end']]
        else:
            found_word = None
        if entity['mention'] != found_word:
            entities.remove(entity)

    corpus["entities"] = entities

    return corpus


def main():
    reddit = rddt.Reddit()
    database_manager = db.DatabaseManager()
    tagme_manager = TagmeManager(rho=0.1)
    processor_manager = TextProcessor()

    post_list: list[rddt.RedditPost] = reddit.get_hot_posts("Trump")
    post_list = processor_manager.clean_posts(post_list)
    database_manager.insert_posts(post_list)
    post_all_annotations, post_all_humans, title_all_annotations, title_all_humans = tagme_manager.tag_posts(post_list)
    print(post_all_humans)
    print(title_all_humans)


def bg_main():
    reddit = rddt.Reddit()
    database_manager = db.DatabaseManager()
    post_list: list[rddt.RedditPost] = reddit.get_hot_posts("PoliticalDiscussion", limit=2)
    corpus_list: list = []
    for post in post_list:
        corpus_list.append(generate_corpus(Platform.REDDIT, "PoliticalDiscussion", post.id, post.title, post.selftext))

    database_manager.insert_posts(post_list)
    database_manager.insert_corpuses(corpus_list)
    print(json.dumps(corpus_list, indent=2))


if __name__ == "__main__":
    # main()
    bg_main()
