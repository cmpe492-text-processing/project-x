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

    def tag_posts(self, posts):
        all_annotations = []
        all_humans = []
        for post in posts:
            post_annotations, all_humans = self.process_post(post)
            all_annotations.append(post_annotations)

        return all_annotations, all_humans

    def process_post(self, post):
        selftext = post.selftext.lower()
        print(selftext)

        annotations = tagme.annotate(selftext)
        humans = []
        for ann in annotations.get_annotations(self.rho):
            wikidata_item_info = get_wikidata_item_info(get_wikidata_url_from_curid(ann.entity_id))
            if 'Q5' in wikidata_item_info['P31']:
                human = {
                    'begin': ann.begin,
                    'end': ann.end,
                    'entity_id': ann.entity_id,
                    'entity_title': ann.entity_title,
                    'relatedness_scores': []
                }
                humans.append(human)

        for human in humans:
            relatedness_scores = []
            for annotation in annotations.get_annotations(self.rho):
                if annotation.entity_id != human['entity_id']:
                    relations = tagme.relatedness_wid((human['entity_id'], annotation.entity_id))
                    for relatedness in relations.relatedness:
                        relatedness_scores.append({
                            'begin': annotation.begin,
                            'end': annotation.end,
                            'entity_id': annotation.entity_id,
                            'entity_title': annotation.entity_title,
                            'score': relatedness.rel
                        })
            human['relatedness_scores'] = relatedness_scores

        return annotations, humans
