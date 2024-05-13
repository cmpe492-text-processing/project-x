from flask import request, render_template, jsonify
from app.services.tagging import get_basic_info, get_wikidata_info


def init_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/search/', methods=['GET'])
    def search():
        query = request.args.get('q', '').strip()

        if query.strip() == '':
            return jsonify({'error': 'Empty query'}), 204

        if query.startswith('Q') and query[1:].isdigit():
            # Fetch label from Wikidata
            return jsonify(get_wikidata_info(query)), 200

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


