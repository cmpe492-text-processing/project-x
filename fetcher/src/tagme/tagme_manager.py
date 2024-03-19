import os
from dotenv import load_dotenv
import tagme
import requests


def get_wikidata_url_from_curid(curid):
    wikipedia_api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "pageprops",
        "pageids": curid,
        "format": "json"
    }
    response = requests.get(wikipedia_api_url, params=params)
    data = response.json()
    try:
        wikidata_item_id = data["query"]["pages"][str(curid)]["pageprops"]["wikibase_item"]
        wikidata_url = f"https://www.wikidata.org/wiki/{wikidata_item_id}"
        return wikidata_url
    except KeyError as e:
        return None


class TagmeManager:

    def __init__(self, rho):
        load_dotenv('../.env')
        self.api_key = os.getenv('TAGME_API_KEY')
        tagme.GCUBE_TOKEN = self.api_key
        self.rho = rho

    def process_posts(self, posts):
        all_annotations = []
        for post in posts:
            post_annotations = self.process_post(post)
            all_annotations.append(post_annotations)
        return all_annotations

    def process_post(self, post):
        selftext = post.selftext.lower()

        annotations = tagme.annotate(selftext)
        print(selftext)
        for ann in annotations.get_annotations(self.rho):
            print(ann.begin)
            print(ann.end)
            print(ann.entity_id)
            print(ann.entity_title)
            print(ann.score)
            print(ann.mention)
        return annotations
