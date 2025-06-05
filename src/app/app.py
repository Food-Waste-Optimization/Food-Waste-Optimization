"""Create and configure Flask-app object with CORS-support."""

from flask import Flask
from flask_cors import CORS
from loguru import logger

from src import config

from .routes import blueprint

logger.info(f"Work at FLASK_ENV: {config.FLASK_ENV}")


def create_app():
    """Create and configure Flask-app object with CORS-support.

    Returns:
        Flask: Flask-app object.
    """

    match config.FLASK_ENV:
        case "development":
            template_dir = "src/frontend/dist"
        case "production":
            template_dir = "/build/dist"
        case _:
            raise NotImplementedError()

    app = Flask(
        __name__,
        static_url_path="/",
        static_folder=template_dir,
        template_folder=template_dir,
    )
    CORS(app)
    app.register_blueprint(blueprint)

    configuration_mode = config.FLASK_ENV
    app.config.from_object(config.set_configuration(configuration_mode))

    return app


app = create_app()
