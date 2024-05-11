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
