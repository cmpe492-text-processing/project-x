import os
from dotenv import load_dotenv
import tagme
import requests
from tagme import Annotation


def get_wikidata_url_from_curid(curid):
    params = {
        "action": "query",
        "prop": "pageprops",
        "pageids": curid,
        "format": "json"
    }
    wikipedia_api_url = "https://en.wikipedia.org/w/api.php"

    response = requests.get(wikipedia_api_url, params=params)
    data = response.json()
    try:
        wikidata_item_id = data["query"]["pages"][str(curid)]["pageprops"]["wikibase_item"]
        return wikidata_item_id
    except KeyError as e:
        print(f"Error {e} fetching Wikidata URL from cur-id {curid}.")
        return None


def get_wikidata_item_info(wikidata_item_id):
    attempts = 0
    max_attempts = 5
    wikidata_entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_item_id}.json"

    while attempts < max_attempts:
        response = requests.get(wikidata_entity_url)
        if response.status_code == 200:
            data = response.json()
            item_info = {
                'P31': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P31', []),
                'P21': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P21', []),
                'P17': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P17', [])
            }
            return item_info
        else:
            attempts += 1
            print(f"Attempt {attempts}/{max_attempts} failed with status code {response.status_code}. Retrying...")

    print("Error fetching Wikidata API data after maximum attempts.")
    return {}


def get_wikidata_item_info_general(wikidata_item_id):
    attempts = 0
    max_attempts = 5
    wikidata_entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_item_id}.json"

    while attempts < max_attempts:
        response = requests.get(wikidata_entity_url)
        if response.status_code == 200:
            data = response.json()
            # https://hay.toolforge.org/propbrowse/
            item_info = {
                'instance of': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P31', []),
                'sex or gender': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P21', []),
                'country': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P17', []),
                'occupation': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P106', []),
                'given name': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P735', []),
                'date of birth': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P569', []),
                'date of death': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P570', []),
                'place of birth': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P19', []),
                'place of death': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P20', []),
                'country of citizenship': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get(
                    'P27', []),
                'educated at': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P69', []),
                'employer': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P108', []),
                'award received': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P166', []),
                'position held': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P39', []),
                'work location': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P937', []),
                'field of work': data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P101', []),
            }

            return item_info
        else:
            attempts += 1
            print(f"Attempt {attempts}/{max_attempts} failed with status code {response.status_code}. Retrying...")

    print("Error fetching Wikidata API data after maximum attempts.")
    return {}


class TagmeManager:

    def __init__(self, rho):
        load_dotenv('../.env')
        self.api_key = os.getenv('TAGME_API_KEY')
        tagme.GCUBE_TOKEN = self.api_key
        self.rho = rho

    def tag_posts(self, posts):
        post_all_annotations = []
        post_all_humans = []
        title_all_annotations = []
        title_all_humans = []
        for post in posts:
            post_annotations, post_humans = self.process_text(post.cleaned_selftext)
            title_annotations, title_humans = self.process_text(post.cleaned_title)
            post_all_annotations.append(post_annotations)
            post_all_humans.append(post_humans)
            title_all_annotations.append(title_annotations)
            title_all_humans.append(title_humans)

        return post_all_annotations, post_all_humans, title_all_annotations, title_all_humans

    @staticmethod
    def get_annotation_info(annotation):
        info = get_wikidata_item_info_general(get_wikidata_url_from_curid(annotation.entity_id))

        final = {}
        for key, value in info.items():
            if len(value) == 0:
                continue

            for item in value:
                try:
                    item = item['mainsnak']['datavalue']['value']['id']
                except KeyError:
                    continue

                if key not in final:
                    final[key] = []

                if item not in final[key]:
                    final[key].append(item)

        """
            for item in value:
                item = item['mainsnak']['datavalue']['value']['id']
                if key not in final:
                    final[key] = []
                name = TagmeManager.get_wikidata_name(item)
                if name is not None:
                    final[key].append((item, name))
        """

        return final

    def process_text(self, selftext):
        annotations = tagme.annotate(selftext)
        print(selftext)
        humans = []

        if annotations is None:
            print(f"No annotations found for the text {selftext}.")
            return [], []

        for ann in annotations.get_annotations(self.rho):
            wikidata_item_info = get_wikidata_item_info(get_wikidata_url_from_curid(ann.entity_id))
            if wikidata_item_info is not None and 'P31' in wikidata_item_info:
                for item in wikidata_item_info['P31']:
                    if 'datavalue' in item['mainsnak'] and 'value' in item['mainsnak']['datavalue']:
                        if item['mainsnak']['datavalue']['value']['id'] == 'Q5':
                            human = {
                                'begin': ann.begin,
                                'end': ann.end,
                                'entity_id': ann.entity_id,
                                'entity_title': ann.entity_title,
                                'relatedness_scores': []
                            }
                            print(f"Human entity found: {human}")
                            humans.append(human)

        for human in humans:
            print(f"Processing relatedness scores for human entity {human['entity_title']}.")

            relatedness_scores = []
            for other_human in humans:
                print(f"Processing relatedness scores for other human entity {other_human['entity_title']}.")
                if other_human['entity_id'] != human['entity_id']:
                    relations = tagme.relatedness_wid((human['entity_id'], other_human['entity_id']))
                    for relatedness in relations.relatedness:
                        if relatedness.rel > 0.25:
                            relatedness_scores.append({
                                'begin': other_human['begin'],
                                'end': other_human['end'],
                                'entity_id': other_human['entity_id'],
                                'entity_title': other_human['entity_title'],
                                'score': relatedness.rel
                            })
            human['relatedness_scores'] = relatedness_scores

        return annotations, humans

    def tag_text(self, txt: str) -> list[Annotation]:
        try:
            return tagme.annotate(txt).get_annotations(self.rho)
        except Exception as e:
            print(f"Error tagging text: {e.__str__()}")
            return []

    @staticmethod
    def get_wikidata_name(curid):
        attempts = 0
        max_attempts = 5
        wikidata_entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{curid}.json"

        while attempts < max_attempts:
            response = requests.get(wikidata_entity_url)
            if response.status_code == 200:
                data = response.json()
                return data['entities'][curid]['labels']['en']['value']
            else:
                attempts += 1

        return None

