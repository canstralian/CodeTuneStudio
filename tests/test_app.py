import unittest
from unittest.mock import MagicMock, mock_open, patch

import pytest

from app import MLFineTuningApp


class TestMLFineTuningApp(unittest.TestCase):
    def setUp(self) -> None:
        self.app = MLFineTuningApp()

    @patch("app.os.environ.get")
    def test_configure_database(self, mock_env) -> None:
        mock_env.return_value = "sqlite:///test.db"
        self.app._configure_database()
        assert (
            self.app.flask_app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///test.db"
        )

    @patch("app.init_db")
    @patch("app.time.sleep")
    def test_initialize_database_with_retry_success(
        self, mock_sleep, mock_init_db
    ) -> None:
        mock_init_db.return_value = None
        self.app._initialize_database_with_retry()
        mock_init_db.assert_called_once()

    @patch("app.init_db")
    @patch("app.time.sleep")
    def test_initialize_database_with_retry_failure_then_fallback(
        self, mock_sleep, mock_init_db
    ) -> None:
        mock_init_db.side_effect = [Exception("DB error"), None]
        self.app._initialize_database_with_retry()
        assert (
            self.app.flask_app.config["SQLALCHEMY_DATABASE_URI"]
            == "sqlite:///fallback.db"
        )

    @patch("app.db.session")
    def test_session_scope_commit(self, mock_session) -> None:
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        with self.app.session_scope():
            pass
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()

    @patch("app.db.session")
    def test_session_scope_rollback(self, mock_session) -> None:
        mock_session_instance = MagicMock()
        mock_session_instance.commit.side_effect = Exception("Commit error")
        mock_session.return_value = mock_session_instance
        with pytest.raises(Exception), self.app.session_scope():
            pass
        mock_session_instance.rollback.assert_called_once()
        mock_session_instance.close.assert_called_once()

    @patch("app.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="css content")
    def test_load_custom_css_success(self, mock_file, mock_exists) -> None:
        mock_exists.return_value = True
        result = self.app._load_custom_css()
        assert result == "css content"

    @patch("app.os.path.exists")
    def test_load_custom_css_not_found(self, mock_exists) -> None:
        mock_exists.return_value = False
        result = self.app._load_custom_css()
        assert result is None

    @patch("app.st.set_page_config")
    @patch("app.st.markdown")
    def test_configure_streamlit(self, mock_markdown, mock_set_page_config) -> None:
        self.app._configure_streamlit()
        mock_set_page_config.assert_called_once()

    @patch("app.registry.clear_tools")
    @patch("app.registry.discover_tools")
    @patch("app.registry.list_tools")
    @patch("app.os.path.abspath")
    @patch("app.os.path.join")
    @patch("app.os.path.dirname")
    def test_load_plugins(
        self,
        mock_dirname,
        mock_join,
        mock_abspath,
        mock_list_tools,
        mock_discover,
        mock_clear,
    ) -> None:
        mock_list_tools.return_value = ["tool1", "tool2"]
        self.app._load_plugins()
        mock_clear.assert_called_once()
        mock_discover.assert_called_once()

    @patch("app.registry.list_tools")
    @patch("app.st.sidebar")
    @patch("app.st.title")
    @patch("app.st.markdown")
    @patch("app.st.text")
    @patch("app.st.warning")
    def test_setup_sidebar_with_tools(
        self,
        mock_warning,
        mock_text,
        mock_markdown,
        mock_title,
        mock_sidebar,
        mock_list_tools,
    ) -> None:
        mock_list_tools.return_value = ["tool1"]
        self.app.setup_sidebar()
        mock_title.assert_called_once_with("ML Model Fine-tuning")
        mock_text.assert_called_once_with("✓ tool1")

    @patch("app.registry.list_tools")
    @patch("app.st.sidebar")
    @patch("app.st.title")
    @patch("app.st.markdown")
    @patch("app.st.warning")
    def test_setup_sidebar_no_tools(
        self, mock_warning, mock_markdown, mock_title, mock_sidebar, mock_list_tools
    ) -> None:
        mock_list_tools.return_value = []
        self.app.setup_sidebar()
        mock_warning.assert_called_once_with("No plugins available")

    @patch("app.st.markdown")
    def test_render_navigation(self, mock_markdown) -> None:
        self.app._render_navigation()
        mock_markdown.assert_called_once()

    def test_save_training_config_invalid_type(self) -> None:
        result = self.app.save_training_config("not a dict", "dataset")
        assert result is None

    def test_save_training_config_missing_fields(self) -> None:
        config = {"model_type": "test"}
        result = self.app.save_training_config(config, "dataset")
        assert result is None

    @patch("app.TrainingConfig")
    @patch("app.db.session")
    def test_save_training_config_success(
        self, mock_session, mock_training_config
    ) -> None:
        config = {
            "model_type": "test",
            "batch_size": 16,
            "learning_rate": 0.001,
            "epochs": 10,
            "max_seq_length": 512,
            "warmup_steps": 100,
        }
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_config_instance = MagicMock()
        mock_config_instance.id = 1
        mock_training_config.return_value = mock_config_instance
        result = self.app.save_training_config(config, "dataset")
        assert result == 1

    @patch("app.st.session_state")
    @patch("app.st.markdown")
    @patch("app.st.expander")
    @patch("app.dataset_browser")
    @patch("app.validate_dataset_name")
    @patch("app.training_parameters")
    @patch("app.validate_config")
    @patch("app.training_monitor")
    @patch("app.experiment_compare")
    @patch("app.st.button")
    @patch("app.st.json")
    @patch("app.st.error")
    @patch("app.st.warning")
    def test_run_success(
        self,
        mock_warning,
        mock_error,
        mock_json,
        mock_button,
        mock_experiment_compare,
        mock_training_monitor,
        mock_validate_config,
        mock_training_parameters,
        mock_validate_dataset_name,
        mock_dataset_browser,
        mock_expander,
        mock_markdown,
        mock_session_state,
    ) -> None:
        mock_session_state.__contains__ = MagicMock(return_value=True)
        mock_session_state.__getitem__ = MagicMock(return_value="main")
        mock_dataset_browser.return_value = "dataset"
        mock_validate_dataset_name.return_value = True
        mock_training_parameters.return_value = {
            "model_type": "test",
            "batch_size": 16,
            "learning_rate": 0.001,
            "epochs": 10,
            "max_seq_length": 512,
            "warmup_steps": 100,
        }
        mock_validate_config.return_value = []
        mock_button.return_value = False
        with patch.object(self.app, "save_training_config", return_value=1):
            with patch.object(self.app, "setup_sidebar"):
                self.app.run()
        mock_markdown.assert_called()

        @patch("app.os.path.exists")
        @patch("builtins.open", new_callable=mock_open)
        def test_load_custom_css_read_error(self, mock_file, mock_exists) -> None:
            mock_exists.return_value = True
            mock_file.side_effect = Exception("Read error")
            result = self.app._load_custom_css()
            assert result is None

        @patch("app.st.set_page_config")
        def test_configure_streamlit_failure(self, mock_set_page_config) -> None:
            mock_set_page_config.side_effect = Exception("Config error")
            with pytest.raises(RuntimeError):
                self.app._configure_streamlit()

        @patch("app.registry.clear_tools")
        @patch("app.registry.discover_tools")
        def test_load_plugins_clear_failure(self, mock_discover, mock_clear) -> None:
            mock_clear.side_effect = Exception("Clear error")
            self.app._load_plugins()
            mock_discover.assert_called_once()

        @patch("app.registry.discover_tools")
        def test_load_plugins_discover_failure(self, mock_discover) -> None:
            mock_discover.side_effect = Exception("Discover error")
            self.app._load_plugins()

        @patch("app.TrainingConfig")
        @patch("app.db.session")
        def test_save_training_config_db_error(
            self, mock_session, mock_training_config
        ) -> None:
            config = {
                "model_type": "test",
                "batch_size": 16,
                "learning_rate": 0.001,
                "epochs": 10,
                "max_seq_length": 512,
                "warmup_steps": 100,
            }
            mock_session_instance = MagicMock()
            mock_session_instance.add.side_effect = Exception("DB error")
            mock_session.return_value = mock_session_instance
            result = self.app.save_training_config(config, "dataset")
            assert result is None

        @patch("app.st.session_state")
        @patch("app.st.markdown")
        @patch("app.st.expander")
        @patch("app.dataset_browser")
        @patch("app.validate_dataset_name")
        @patch("app.st.warning")
        def test_run_invalid_dataset(
            self,
            mock_warning,
            mock_validate_dataset_name,
            mock_dataset_browser,
            mock_expander,
            mock_markdown,
            mock_session_state,
        ) -> None:
            mock_session_state.__contains__ = MagicMock(return_value=True)
            mock_session_state.__getitem__ = MagicMock(return_value="main")
            mock_dataset_browser.return_value = None
            with patch.object(self.app, "setup_sidebar"):
                self.app.run()
            mock_warning.assert_called_with("Please select a valid dataset to continue")

        @patch("app.st.session_state")
        @patch("app.st.markdown")
        @patch("app.st.expander")
        @patch("app.dataset_browser")
        @patch("app.validate_dataset_name")
        @patch("app.training_parameters")
        @patch("app.st.error")
        def test_run_invalid_config_format(
            self,
            mock_error,
            mock_training_parameters,
            mock_validate_dataset_name,
            mock_dataset_browser,
            mock_expander,
            mock_markdown,
            mock_session_state,
        ) -> None:
            mock_session_state.__contains__ = MagicMock(return_value=True)
            mock_session_state.__getitem__ = MagicMock(return_value="main")
            mock_dataset_browser.return_value = "dataset"
            mock_validate_dataset_name.return_value = True
            mock_training_parameters.return_value = "not a dict"
            with patch.object(self.app, "setup_sidebar"):
                self.app.run()
            mock_error.assert_called_with("Invalid configuration format")

        @patch("app.st.session_state")
        @patch("app.st.markdown")
        @patch("app.st.expander")
        @patch("app.dataset_browser")
        @patch("app.validate_dataset_name")
        @patch("app.training_parameters")
        @patch("app.validate_config")
        @patch("app.st.error")
        def test_run_config_validation_errors(
            self,
            mock_error,
            mock_validate_config,
            mock_training_parameters,
            mock_validate_dataset_name,
            mock_dataset_browser,
            mock_expander,
            mock_markdown,
            mock_session_state,
        ) -> None:
            mock_session_state.__contains__ = MagicMock(return_value=True)
            mock_session_state.__getitem__ = MagicMock(return_value="main")
            mock_dataset_browser.return_value = "dataset"
            mock_validate_dataset_name.return_value = True
            mock_training_parameters.return_value = {
                "model_type": "test",
                "batch_size": 16,
                "learning_rate": 0.001,
                "epochs": 10,
                "max_seq_length": 512,
                "warmup_steps": 100,
            }
            mock_validate_config.return_value = ["Error 1", "Error 2"]
            with patch.object(self.app, "setup_sidebar"):
                self.app.run()
            assert mock_error.call_count == 2

        @patch("app.st.session_state")
        @patch("app.st.markdown")
        @patch("app.st.expander")
        @patch("app.dataset_browser")
        @patch("app.validate_dataset_name")
        @patch("app.training_parameters")
        @patch("app.validate_config")
        @patch("app.st.error")
        def test_run_save_config_failure(
            self,
            mock_error,
            mock_validate_config,
            mock_training_parameters,
            mock_validate_dataset_name,
            mock_dataset_browser,
            mock_expander,
            mock_markdown,
            mock_session_state,
        ) -> None:
            mock_session_state.__contains__ = MagicMock(return_value=True)
            mock_session_state.__getitem__ = MagicMock(return_value="main")
            mock_dataset_browser.return_value = "dataset"
            mock_validate_dataset_name.return_value = True
            mock_training_parameters.return_value = {
                "model_type": "test",
                "batch_size": 16,
                "learning_rate": 0.001,
                "epochs": 10,
                "max_seq_length": 512,
                "warmup_steps": 100,
            }
            mock_validate_config.return_value = []
            with patch.object(self.app, "setup_sidebar"):
                with patch.object(self.app, "save_training_config", return_value=None):
                    self.app.run()
            mock_error.assert_called_with(
                "Failed to save configuration. Please try again."
            )

        @patch("app.st.session_state")
        @patch("app.st.markdown")
        @patch("app.st.expander")
        @patch("app.dataset_browser")
        @patch("app.validate_dataset_name")
        @patch("app.training_parameters")
        @patch("app.validate_config")
        @patch("app.st.error")
        def test_run_general_exception(
            self,
            mock_error,
            mock_validate_config,
            mock_training_parameters,
            mock_validate_dataset_name,
            mock_dataset_browser,
            mock_expander,
            mock_markdown,
            mock_session_state,
        ) -> None:
            mock_session_state.__contains__ = MagicMock(return_value=True)
            mock_session_state.__getitem__ = MagicMock(return_value="main")
            mock_dataset_browser.side_effect = Exception("General error")
            with patch.object(self.app, "setup_sidebar"):
                self.app.run()
            mock_error.assert_called_with(
                "An unexpected error occurred. Please try again or contact support."
            )

        @patch("app.MLFineTuningApp")
        @patch("app.st.error")
        def test_main_success(self, mock_st_error, mock_app_class) -> None:
            mock_app_instance = MagicMock()
            mock_app_class.return_value = mock_app_instance
            main()
            mock_app_instance.run.assert_called_once()

        @patch("app.MLFineTuningApp")
        @patch("app.st.error")
        def test_main_failure(self, mock_st_error, mock_app_class) -> None:
            mock_app_class.side_effect = Exception("Init error")
            main()
            mock_st_error.assert_called_with(
                "A critical error occurred. Please reload the page or contact support."
            )


if __name__ == "__main__":
    unittest.main()
