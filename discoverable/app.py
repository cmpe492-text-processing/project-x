from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# from app.models import *
from app.routes import init_routes

with app.app_context():
    init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
