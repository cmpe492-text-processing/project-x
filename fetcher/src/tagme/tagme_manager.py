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
        # wikidata_url = f"https://www.wikidata.org/wiki/{wikidata_item_id}"
        return wikidata_item_id
    except KeyError as e:
        return None


def get_wikidata_item_info(wikidata_item_id):
    wikidata_entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_item_id}.json"
    response = requests.get(wikidata_entity_url)
    if response.status_code != 200:
        print("Error fetching Wikidata API data.")
        return {}

    data = response.json()
    item_info = {
        'P31': [],  # Instance of
        'P21': [],  # Sex or gender
        'P17': []  # Country
    }

    claims = data['entities'][wikidata_item_id].get('claims', {})

    for prop in ['P31', 'P21', 'P17']:
        if prop in claims:
            for claim in claims[prop]:
                if 'datavalue' in claim['mainsnak']:
                    claim_value = claim['mainsnak']['datavalue']['value']
                    if isinstance(claim_value, dict) and 'id' in claim_value:
                        item_info[prop].append(claim_value['id'])

    return item_info

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
            print(get_wikidata_url_from_curid(ann.entity_id))
            wikidata_item_info = get_wikidata_item_info(get_wikidata_url_from_curid(ann.entity_id))
            print(wikidata_item_info)
            print(ann.entity_title)
            print(ann.score)
            print(ann.mention)
        return annotations
