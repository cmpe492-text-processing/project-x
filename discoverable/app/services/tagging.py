import requests
from tagme import Annotation, annotate
from nltk.sentiment import SentimentIntensityAnalyzer


def get_basic_info(text: str) -> dict:
    """
    Extracts the entities in the given text. Does basic sentiment analysis for the whole text.

    :param text:    Input String
    :return:        {
                        text: str,
                        entities: {
                                    name: str,
                                    mention: str,
                                    begin: int,
                                    end: int,
                                    confidence: float,
                                    wiki_id: float,
                                    wiki_info: dict
                                    },
                        scores: {
                            compound: float,
                            neu: float,
                            pos: float,
                            neg: float
                            }
                    }
    """
    text = text.strip()
    entities: list[dict] = []
    annotations: list[Annotation] = annotate(text).get_annotations(0.15)
    for annotation in annotations:
        entity = {
            "name": annotation.entity_title,
            "mention": annotation.mention,
            "begin": annotation.begin,
            "end": annotation.end,
            "confidence": annotation.score,
            "wiki_id": annotation.entity_id,
            "wiki_info": {},
        }

        # item_info = {}
        # attempts = 0
        # max_attempts = 5
        # eid = annotation.entity_id
        # wikidata_entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{eid}.json"
        # while attempts < max_attempts:
        #     response = requests.get(wikidata_entity_url)
        #     if response.status_code == 200:
        #         data = response.json()
        #         item_info = {
        #             'instance of': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P31', []),
        #             'sex or gender': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P21',
        #                                                                                                       []),
        #             'country': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P17', []),
        #             'occupation': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P106', []),
        #             'given name': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P735', []),
        #             'date of birth': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P569',
        #                                                                                                       []),
        #             'date of death': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P570',
        #                                                                                                       []),
        #             'place of birth': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P19',
        #                                                                                                        []),
        #             'place of death': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P20',
        #                                                                                                        []),
        #             'country of citizenship': data.get('entities', {}).get(eid, {}).get('claims', {}).get(
        #                 'P27', []),
        #             'educated at': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P69', []),
        #             'employer': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P108', []),
        #             'award received': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P166',
        #                                                                                                        []),
        #             'position held': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P39',
        #                                                                                                       []),
        #             'work location': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P937',
        #                                                                                                       []),
        #             'field of work': data.get('entities', {}).get(eid, {}).get('claims', {}).get('P101',
        #                                                                                                       []),
        #         }

        #         item_info = {k: v for k, v in item_info.items() if v is not None}
        #         break
        #     else:
        #         attempts += 1
        #         print(f"Attempt {attempts}/{max_attempts} failed with status code {response.status_code}. Retrying...")

        # entity['wiki_info'] = item_info
        entities.append(entity)

    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)

    return {"text": text, "entities": entities, "scores": scores}


def get_wikidata_info(text: str) -> dict:
    return {"B": "G"}
