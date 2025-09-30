import os
import unittest
from unittest.mock import MagicMock, patch

from db_check import check_database


class TestCheckDatabase(unittest.TestCase):
    @patch("db_check.db")
    @patch("db_check.init_db")
    @patch("db_check.Flask")
    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///test.db"})
    def test_successful_connection(
        self, mock_flask: MagicMock, mock_init_db: MagicMock, mock_db: MagicMock
    ) -> None:
        # Mock Flask app and context
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        mock_context = MagicMock()
        mock_app.app_context.return_value.__enter__.return_value = mock_context
        mock_app.app_context.return_value.__exit__.return_value = None

        # Mock db.session.execute to return 1
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_execute = MagicMock()
        mock_session.execute.return_value = mock_execute
        mock_execute.scalar.return_value = 1

        result = check_database()
        self.assertTrue(result)
        mock_init_db.assert_called_once_with(mock_app)
        mock_session.execute.assert_called_once_with("SELECT 1")

    @patch("db_check.db")
    @patch("db_check.init_db")
    @patch("db_check.Flask")
    @patch.dict(os.environ, {}, clear=True)  # No DATABASE_URL set
    def test_default_database_url(
        self, mock_flask: MagicMock, _mock_init_db: MagicMock, mock_db: MagicMock
    ) -> None:
        # Mock Flask app and context
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        mock_context = MagicMock()
        mock_app.app_context.return_value.__enter__.return_value = mock_context
        mock_app.app_context.return_value.__exit__.return_value = None

        # Mock db.session.execute to return 1
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_execute = MagicMock()
        mock_session.execute.return_value = mock_execute
        mock_execute.scalar.return_value = 1

        result = check_database()
        self.assertTrue(result)
        # Check that default URL is used
        self.assertEqual(
            mock_app.config["SQLALCHEMY_DATABASE_URI"], "sqlite:///database.db"
        )

    @patch("db_check.db")
    @patch("db_check.init_db")
    @patch("db_check.Flask")
    def test_connection_failure_exception(
        self, mock_flask: MagicMock, _mock_init_db: MagicMock, mock_db: MagicMock
    ) -> None:
        # Mock Flask app and context
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        mock_context = MagicMock()
        mock_app.app_context.return_value.__enter__.return_value = mock_context
        mock_app.app_context.return_value.__exit__.return_value = None

        # Mock db.session.execute to raise an exception
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_session.execute.side_effect = Exception("Connection error")

        result = check_database()
        self.assertFalse(result)

    @patch("db_check.db")
    @patch("db_check.init_db")
    @patch("db_check.Flask")
    def test_unexpected_query_result(
        self, mock_flask: MagicMock, _mock_init_db: MagicMock, mock_db: MagicMock
    ) -> None:
        # Mock Flask app and context
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        mock_context = MagicMock()
        mock_app.app_context.return_value.__enter__.return_value = mock_context
        mock_app.app_context.return_value.__exit__.return_value = None

        # Mock db.session.execute to return unexpected result
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_execute = MagicMock()
        mock_session.execute.return_value = mock_execute
        mock_execute.scalar.return_value = 0  # Not 1

        result = check_database()
        self.assertFalse(result)

    @patch("db_check.db")
    @patch("db_check.init_db")
    @patch("db_check.Flask")
    @patch("builtins.print")
    def test_successful_connection_prints(
        self,
        _mock_print: MagicMock,
        mock_flask: MagicMock,
        _mock_init_db: MagicMock,
        mock_db: MagicMock,
    ) -> None:
        # Mock Flask app and context
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        mock_context = MagicMock()
        mock_app.app_context.return_value.__enter__.return_value = mock_context
        mock_app.app_context.return_value.__exit__.return_value = None

        # Mock db.session.execute to return 1
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_execute = MagicMock()
        mock_session.execute.return_value = mock_execute
        mock_execute.scalar.return_value = 1

        result = check_database()
        self.assertTrue(result)
        # Check print calls
        expected_calls = [
            unittest.mock.call("Checking database connection..."),
            unittest.mock.call("Using database URL: sqlite:///database.db"),
            unittest.mock.call("Database connection successful!"),
            unittest.mock.call("Database connection successful!"),
        ]
        _mock_print.assert_has_calls(expected_calls)

    @patch("db_check.db")
    @patch("db_check.init_db")
    @patch("db_check.Flask")
    @patch("builtins.print")
    def test_connection_failure_prints(
        self,
        _mock_print: MagicMock,
        mock_flask: MagicMock,
        _mock_init_db: MagicMock,
        mock_db: MagicMock,
    ) -> None:
        # Mock Flask app and context
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        mock_context = MagicMock()
        mock_app.app_context.return_value.__enter__.return_value = mock_context
        mock_app.app_context.return_value.__exit__.return_value = None

        # Mock db.session.execute to raise an exception
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_session.execute.side_effect = Exception("Connection error")

        result = check_database()
        self.assertFalse(result)
        # Check print calls
        expected_calls = [
            unittest.mock.call("Checking database connection..."),
            unittest.mock.call("Using database URL: sqlite:///database.db"),
            unittest.mock.call("Database connection failed: Connection error"),
        ]
        _mock_print.assert_has_calls(expected_calls)

    @patch("db_check.db")
    @patch("db_check.init_db")
    @patch("db_check.Flask")
    @patch("builtins.print")
    def test_unexpected_result_prints(
        self,
        _mock_print: MagicMock,
        mock_flask: MagicMock,
        _mock_init_db: MagicMock,
        mock_db: MagicMock,
    ) -> None:
        # Mock Flask app and context
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        mock_context = MagicMock()
        mock_app.app_context.return_value.__enter__.return_value = mock_context
        mock_app.app_context.return_value.__exit__.return_value = None

        # Mock db.session.execute to return unexpected result
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_execute = MagicMock()
        mock_session.execute.return_value = mock_execute
        mock_execute.scalar.return_value = 0  # Not 1

        result = check_database()
        self.assertFalse(result)
        # Check print calls
        expected_calls = [
            unittest.mock.call("Checking database connection..."),
            unittest.mock.call("Using database URL: sqlite:///database.db"),
            unittest.mock.call("Database connection check returned unexpected result"),
        ]
        _mock_print.assert_has_calls(expected_calls)

    @patch("db_check.db")
    @patch("db_check.init_db")
    @patch("db_check.Flask")
    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost/db"})
    @patch("builtins.print")
    def test_custom_database_url_prints(
        self,
        _mock_print: MagicMock,
        mock_flask: MagicMock,
        _mock_init_db: MagicMock,
        mock_db: MagicMock,
    ) -> None:
        # Mock Flask app and context
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        mock_context = MagicMock()
        mock_app.app_context.return_value.__enter__.return_value = mock_context
        mock_app.app_context.return_value.__exit__.return_value = None

        # Mock db.session.execute to return 1
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_execute = MagicMock()
        mock_session.execute.return_value = mock_execute
        mock_execute.scalar.return_value = 1

        result = check_database()
        self.assertTrue(result)
        # Check that custom URL is printed
        _mock_print.assert_any_call(
            "Using database URL: postgresql://user:pass@localhost/db"
        )


if __name__ == "__main__":
    unittest.main()
