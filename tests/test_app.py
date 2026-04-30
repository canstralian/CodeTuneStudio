import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Import from the new core.server module
from core.server import MLFineTuningApp, run_app

# Legacy compatibility - map old main to new run_app
main = run_app


class TestMLFineTuningApp(unittest.TestCase):
    def setUp(self) -> None:
        self.app = MLFineTuningApp()

    @patch("core.server.os.environ.get")
    def test_configure_database(self, mock_env) -> None:
        mock_env.return_value = "sqlite:///test.db"
        self.app._configure_database()
        assert (
            self.app.flask_app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///test.db"
        )