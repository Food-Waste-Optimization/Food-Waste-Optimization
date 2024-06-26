import unittest
import os
from flask_testing import TestCase
from src.app.index import app


class TestApp(TestCase):
    def create_app(self):
        return app

    def test_initial_view(self):
        response = self.client.get('/')
        self.assert200(response)


if __name__ == '__main__':
    unittest.main()
