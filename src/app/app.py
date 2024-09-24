"""Create and configure Flask-app object with CORS-support."""

import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from ..config import set_configuration
from .routes import blueprint


def create_app():
    """Create and configure Flask-app object with CORS-support.

    Returns:
        Flask: Flask-app object.
    """

    load_dotenv()
    template_dir = os.path.abspath("src/frontend/dist/")

    app = Flask(
        __name__,
        static_url_path="/",
        static_folder=template_dir,
        template_folder=template_dir,
    )
    CORS(app)
    app.register_blueprint(blueprint)

    configuration_mode = os.getenv("FLASK_ENV")
    app.config.from_object(set_configuration(configuration_mode))

    #
    # init_routes(app)

    return app


app = create_app()
