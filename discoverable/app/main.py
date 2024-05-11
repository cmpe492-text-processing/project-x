from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from app.config import Config
from app.routes.routes import init_routes

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db = SQLAlchemy(app)

with app.app_context():
    init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
