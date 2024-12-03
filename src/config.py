"""Configure different launch modes."""

import os


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
