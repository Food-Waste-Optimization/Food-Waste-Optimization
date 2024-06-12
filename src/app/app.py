from flask import Flask
from flask_cors import CORS
from ..app.db import db
from ..app.routes import init_routes
import os
from dotenv import load_dotenv
from ..config import set_configuration

def create_app():
    load_dotenv()
    app = Flask(__name__, static_url_path='/fwowebserver',
                static_folder='frontend/dist',
                template_folder='frontend/dist')
    CORS(app)

    configuration_mode = os.getenv('FLASK_ENV')
    app.config.from_object(set_configuration(configuration_mode))

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    db.init_app(app)

    init_routes(app)

    return app