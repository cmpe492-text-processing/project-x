from flask import render_template, jsonify


def init_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/search/<string:query>', methods=['GET'])
    def search(query: str):
        return jsonify({
            'input': query,
            'output': 'Hello, World!'
        })
