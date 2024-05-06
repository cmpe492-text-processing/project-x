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


def fetch_label_from_wikidata(q_id):
    """Fetches the label for a given Q value from Wikidata."""
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{q_id}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['entities'][q_id]['labels']['en']['value']
    except requests.RequestException as e:
        print(f"Failed to fetch data from Wikidata: {e}")
        return None


def check_qvalue_and_update_file(q_value):
    """Checks Q value and updates the file if the label is not found."""
    if not q_value:
        return None

    try:
        q_val_ids = []
        for index in range(len(q_value)):
            q_val_ids.append(q_value[index]['mainsnak']['datavalue']['value']['id'])
        print('Q value IDs:', q_val_ids)
    except (IndexError, KeyError) as e:
        print(f"Error occurred while trying to access the Q value: {e}")
        return None

    try:
        with open('q_value_labels.txt', 'r') as fr:
            qval_labels = {}
            for q_val_id in q_val_ids:
                for line in fr:
                    q, label = line.strip().split('\t')
                    if q == q_val_id:
                        qval_labels[q_val_id] = label
                        print(f"Found label for {q_val_id}: {label}")
                        break

    except FileNotFoundError:
        pass  # It's okay if the file doesn't exist yet.

    # If not all q_val_ids labels are not found in the file, fetch them from Wikidata.
    if len(qval_labels) == len(q_val_ids):
        print("All Q value labels found in the file.")
        with open('q_value_labels.txt', 'a') as fw:
            for qval_key, qval_value in qval_labels.items():
                fw.write(f"{qval_key}\t{qval_value}\n")
            print('result', list(qval_labels.values()))
            return list(qval_labels.values())

    else:
        print("Not all Q value labels found in the file. Fetching from Wikidata...")
        remaining_q_val_ids = set(q_val_ids) - set(qval_labels.keys())
        print("Remaining Q value IDs:", remaining_q_val_ids)
        for q_val_id in remaining_q_val_ids:
            label = fetch_label_from_wikidata(q_val_id)
            if label:
                qval_labels[q_val_id] = label
                with open('q_value_labels.txt', 'a') as fw:
                    fw.write(f"{q_val_id}\t{label}\n")
            else:
                qval_labels[q_val_id] = None
        print("result",list(qval_labels.values()))
        return list(qval_labels.values())


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
                'instance of': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P31', [])),
                'sex or gender': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P21', [])),
                'country': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P17', [])),
                'occupation': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P106', [])),
                'given name': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P735', [])),
                'date of birth': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P569', [])),
                'date of death': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P570', [])),
                'place of birth': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P19', [])),
                'place of death': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P20', [])),
                'country of citizenship': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P27', [])),
                'educated at': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P69', [])),
                'employer': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P108', [])),
                'award received': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P166', [])),
                'position held': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P39', [])),
                'work location': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P937', [])),
                'field of work': check_qvalue_and_update_file(data.get('entities', {}).get(wikidata_item_id, {}).get('claims', {}).get('P101', [])),
            }

            item_info = {k: v for k, v in item_info.items() if v is not None}
            return item_info
        else:
            attempts += 1
            print(f"Attempt {attempts}/{max_attempts} failed with status code {response.status_code}. Retrying...")

    print("Error fetching Wikidata API data after maximum attempts.")
    return {}


class TagmeManager:

    def __init__(self, rho):
        load_dotenv('../../.env')
        self.api_key = os.getenv('TAGME_API_KEY')
        tagme.GCUBE_TOKEN = self.api_key
        self.rho = rho

    def tag_posts(self, posts):
        post_all_annotations = []
        title_all_annotations = []

        for post in posts:
            post_annotations = self.process_text(post.cleaned_selftext)
            title_annotations = self.process_text(post.cleaned_title)
            post_all_annotations.append(post_annotations)
            title_all_annotations.append(title_annotations)

        return post_all_annotations, title_all_annotations

    @staticmethod
    def get_annotation_info(annotation):
        return get_wikidata_item_info_general(get_wikidata_url_from_curid(annotation.entity_id))


    @staticmethod
    def process_text(selftext):
        annotations = tagme.annotate(selftext)
        return annotations

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

    @staticmethod
    def relatedness_score(self, wid1, wid2):
        try:
            relations = tagme.relatedness_wid((wid1, wid2))
            for relation in relations.relatedness:
                return relation.rel
        except Exception as e:
            print(f"Error fetching relatedness score: {e}")
            return None
