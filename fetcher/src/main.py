import enum

from fetcher.src import reddit as rddt
import database as db
from fetcher.src.processor import TextProcessor
from fetcher.src.tagme_manager import TagmeManager
import json


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


def print_annotations(tagged: list[Annotation]):
    for annotation in tagged:
        print(annotation)


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
        entities.append(entity)

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
        entities.append(entity)

    text_processor.sentiment_analysis()

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
    post_list: list[rddt.RedditPost] = reddit.get_hot_posts("PoliticalDiscussion", limit=2)
    corpus_list: list = []
    for post in post_list:
        corpus_list.append(generate_corpus(Platform.REDDIT, "PoliticalDiscussion", post.id, post.title, post.selftext))

    print(json.dumps(corpus_list, indent=4))

if __name__ == "__main__":
    # main()
    bg_main()
