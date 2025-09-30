import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from db_check import check_database

class TestCheckDatabase(unittest.TestCase):
    @patch('db_check.db')
    @patch('db_check.init_db')
    @patch('db_check.Flask')
    @patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///test.db'})
    def test_successful_connection(self, mock_flask, mock_init_db, mock_db):
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

    @patch('db_check.db')
    @patch('db_check.init_db')
    @patch('db_check.Flask')
    @patch.dict(os.environ, {}, clear=True)  # No DATABASE_URL set
    def test_default_database_url(self, mock_flask, mock_init_db, mock_db):
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
        self.assertEqual(mock_app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///database.db')

    @patch('db_check.db')
    @patch('db_check.init_db')
    @patch('db_check.Flask')
    def test_connection_failure_exception(self, mock_flask, mock_init_db, mock_db):
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

    @patch('db_check.db')
    @patch('db_check.init_db')
    @patch('db_check.Flask')
    def test_unexpected_query_result(self, mock_flask, mock_init_db, mock_db):
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

if __name__ == '__main__':
    unittest.main()