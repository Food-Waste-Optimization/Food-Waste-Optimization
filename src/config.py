"""Configure different launch modes."""

import os
import sys

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class DefaultConfiguration:
    DEBUG = False
    TESTING = False
    SECRET_KEY = "default"
    CONFIG_MODE = "Default"

    @classmethod
    def set_config_variables(cls):
        CONFIG_MODE = cls.CONFIG_MODE
        SECRET_KEY = cls.SECRET_KEY


class DevelopmentConfiguration(DefaultConfiguration):
    DEBUG = True
    CONFIG_MODE = "Development"
    SECRET_KEY = os.getenv("DEVELOPMENT_KEY")


class TestingConfiguration(DefaultConfiguration):
    TESTING = True
    CONFIG_MODE = "Testing"


class ProductionConfiguration(DefaultConfiguration):
    DEBUG = False
    TESTING = False
    CONFIG_MODE = "Production"
    SECRET_KEY = os.getenv("PRODUCTION_KEY")


config = {
    "development": DevelopmentConfiguration,
    "testing": TestingConfiguration,
    "production": ProductionConfiguration,
    "default": DefaultConfiguration,
}


def set_configuration(env):
    ConfigurationClass = config.get(env, DefaultConfiguration)
    ConfigurationClass.set_config_variables()
    return ConfigurationClass


def _load_env(name: str) -> str:
    env_var = os.getenv(name)
    if env_var is None:
        logger.error(f"Env variable not found: {name}")
        sys.exit(1)

    return env_var


MODEL_TAG = _load_env("MODEL_TAG")
TRAINED_MODELS = _load_env("TRAINED_MODELS")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
