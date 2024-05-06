import enum
import json
import os
import re

from nltk.tokenize import sent_tokenize
from tagme import Annotation

import database as db
from fetcher.src import reddit as rddt
from fetcher.src.processor import TextProcessor
from fetcher.src.tagme_manager import TagmeManager

DEBUG = False


class Platform(enum.Enum):
    REDDIT = "reddit"
    TWITTER = "twitter"

    def __str__(self):
        return self.value


def find_closest_match(original_text, mention, start_index):
    pattern = re.escape(mention)
    for match in re.finditer(pattern, original_text, re.IGNORECASE):
        if abs(match.start() - start_index) <= len(mention):
            return match.start(), match.end()
    return None, None


def adjust_entity_indices(original_text, entity):
    cleaned_begin = entity['begin']
    mention = entity['mention']

    original_index = original_text.find(mention, cleaned_begin - 5 if cleaned_begin > 5 else 0)
    if original_index != -1:
        entity['begin'] = original_index
        entity['end'] = original_index + len(mention)
    else:
        original_begin, original_end = find_closest_match(original_text, mention, cleaned_begin)
        if original_begin is not None and original_end is not None:
            entity['begin'] = original_begin
            entity['end'] = original_end
    return entity


def find_full_sentence(doc, start_idx, end_idx):
    """
    This function finds the full sentence that contains the entity based on starting and ending index.
    """
    sentences = sent_tokenize(doc.text)
    for sentence in sentences:
        if doc.text.find(sentence) <= start_idx and doc.text.find(sentence) + len(sentence) >= end_idx:
            return sentence
    return ""


def generate_corpus(platform: Platform,
                    platform_ext: str,
                    platform_id: str,
                    title: str,
                    body: str) -> dict:
    """
    Generate a corpus from the given parameters.

    :param platform:        platform
    :param platform_ext:    platform extension
    :param platform_id:     platform id
    :param title:           title
    :param body:            body
    :return:                corpus dictionary
    """

    corpus: dict = {"platform": platform.value + "/" + platform_ext if platform_ext else platform.value,
                    "id": platform_id,
                    "title": title,
                    "body": body,
                    "version": 5}

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

    # ENTITIES #

    # create entities with their base tagme information
    entities: list[dict] = []
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
        }

        info = tagme_manager.get_annotation_info(annotation)
        entity['wiki_info'] = info

        adjusted_entity = adjust_entity_indices(title, entity)
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
        }
        info = tagme_manager.get_annotation_info(annotation)
        entity['wiki_info'] = info

        adjusted_entity = adjust_entity_indices(body, entity)
        entities.append(adjusted_entity)

    if len(entities) == 0:
        return corpus

    # filter entities that have their indices adjusted
    for entity in entities:
        if entity['location'] == 'title':
            found_word = title[entity['begin']:entity['end']]
        elif entity['location'] == 'body':
            found_word = body[entity['begin']:entity['end']]
        else:
            found_word = None
        if entity['mention'] != found_word:
            # concurrent modification exception?
            entities.remove(entity)

    # Process title and body with NLP
    title_doc = text_processor.nlp(title)
    body_doc = text_processor.nlp(body)

    for entity in entities:
        if entity['location'] == 'title':
            entity_doc = title_doc
        elif entity['location'] == 'body':
            entity_doc = body_doc
        else:
            continue  # Skip if location is not title or body

        # find the entity itself and its boundaries
        dependent_tokens = []
        for token in entity_doc:
            if entity['begin'] <= token.idx < entity['end']:
                dependent_tokens.append(token)

        if not dependent_tokens:
            continue

        # Extend to full sentence for context
        min_index = min(token.idx for token in dependent_tokens)
        max_index = max(token.idx + len(token.text) for token in dependent_tokens)
        full_sentence = find_full_sentence(entity_doc, min_index, max_index)

        entity['sentence'] = full_sentence

        comp, pos, neg, neu = text_processor.get_sentiment_scores(full_sentence)
        entity['sentiment'] = {
            "compound": comp,
            "positive": pos,
            "negative": neg,
            "neutral": neu
        }

    corpus["entities"] = entities

    # ENTITY_GROUPS #

    entity_groups: list[object] = []
    for entity in entities:
        found = False
        for group in entity_groups:
            if group['sentence'] == entity['sentence']:
                group['entities'].append(entity['wiki_id'])
                found = True
                break
        if not found:
            entity_groups.append({
                "sentence": entity['sentence'],
                "entities": [entity['wiki_id']]
            })

    corpus["entity_groups"] = entity_groups
    return corpus


def main():
    reddit = rddt.Reddit()
    database_manager = db.DatabaseManager()
    tagme_manager = TagmeManager(rho=0.1)
    processor_manager = TextProcessor()

    post_list: list[rddt.RedditPost] = reddit.get_hot_posts("python", limit=2)
    post_list = processor_manager.clean_posts(post_list)
    database_manager.insert_posts(post_list)
    post_all_annotations, title_all_annotations = tagme_manager.tag_posts(post_list)
    print(post_all_annotations)
    print(title_all_annotations)


def other_main():
    reddit = rddt.Reddit()
    database_manager = db.DatabaseManager()
    # subreddits = ["trump", "politics", "elections", "democrats", "republican", "PoliticalDiscussion"]
    subreddits = ['trump']
    for subreddit in subreddits:
        post_list: list[rddt.RedditPost] = reddit.get_hot_posts(subreddit, limit=3)

        corpus_list: list = []
        for post in post_list:
            corpus_list.append(generate_corpus(Platform.REDDIT, subreddit, post.id, post.title, post.selftext))

        if DEBUG:
            print(json.dumps(corpus_list))

        print(
            f"Inserting {len(post_list)} posts and {len(corpus_list)} corpuses into the database related to {subreddit}.")
        print(post_list)
        print(corpus_list)
        database_manager.insert_posts(post_list)
        database_manager.insert_corpuses(corpus_list)


def exporter():
    dbmng = db.DatabaseManager()
    corpuses = dbmng.get_corpuses()
    corpuses = [corp[3] for corp in corpuses]

    raw_dir = '../../data/raw/'
    pattern = re.compile(r'corpus(\d+)\.json')
    files = os.listdir(raw_dir)
    used_nums = {int(match.group(1)) for match in (pattern.match(f) for f in files) if match}
    max_num = max(used_nums) if used_nums else 0
    available_num = next((num for num in range(1, max_num + 2) if num not in used_nums), 1)

    new_filename = f'corpus{available_num}.json'

    with open(raw_dir + new_filename, 'w') as f:
        json.dump(corpuses, f, indent=2)
        print(f'Exported {len(corpuses)} corpuses to {new_filename}')


if __name__ == "__main__":
    other_main()
