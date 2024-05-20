from flask import request, render_template, jsonify
from app.services.tagging import get_basic_info, get_wikidata_info
from nlp.feature_extractor import FeatureExtractor
# from network import Network


def init_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/search/', methods=['GET'])
    def search():
        query = request.args.get('q', '').strip()

        if query.strip() == '':
            return jsonify({'error': 'Empty query'}), 204

        return jsonify(get_basic_info(query)), 200

    @app.route('/histogram/occurrence', methods=['GET'])
    def occurrence_histogram():
        wiki_id = request.args.get('id')

        if wiki_id is None or not wiki_id.isdigit():
            return jsonify({'error': 'Invalid ID'}), 400

        wiki_id = int(wiki_id)

        # Fetch data from database
        if wiki_id == 4848272:
            return jsonify(
                [
                    {
                        "wiki_id": 4848272,
                        "name": "Donald Trump",
                        "occurrence_count": 39
                    },
                    {
                        "wiki_id": 145422,
                        "name": "Joe Biden",
                        "occurrence_count": 2
                    },
                    {
                        "wiki_id": 147301,
                        "name": "Nancy Pelosi",
                        "occurrence_count": 1
                    },
                    {
                        "wiki_id": 703464,
                        "name": "Rob Portman",
                        "occurrence_count": 1
                    }
                ]
            ), 200

        return jsonify([]), 200

    @app.route('/histogram/sentiment', methods=['GET'])
    def sentiment_histogram():
        pass

    # @app.route('/graph', methods=['GET'])
    # def graph():
    #     return jsonify(Network().get_graph()), 200

    @app.route('/wiki-info', methods=['GET'])
    def wiki_info():
        wiki_id = request.args.get('id')

        if wiki_id is None:
            return jsonify({'error': 'Invalid ID'}), 400

        wiki_id = str(wiki_id)

        return jsonify(get_wikidata_info(wiki_id)), 200

    @app.route('/histogram/co-occurrence', methods=['GET'])
    def co_occurrence_histogram():
        wiki_id = request.args.get('id')

        if wiki_id is None or not wiki_id.isdigit():
            return jsonify({'error': 'Invalid ID'}), 400

        wiki_id = int(wiki_id)

        feature_extractor = FeatureExtractor(wiki_id)
        response, most_occurred_entities, main_entity = feature_extractor.create_extracted_features_json_wo_relatedness()

        return jsonify({'most_occurred_entities': most_occurred_entities, 'data': response, 'main_entity': main_entity}), 200


