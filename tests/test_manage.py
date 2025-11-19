from click.testing import CliRunner
from flask.cli import FlaskGroup

from manage import cli


def test_cli_help() -> None:
    """Test that the CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output
    assert "shell" in result.output


def test_cli_is_flask_group() -> None:
    """Test that cli is an instance of FlaskGroup."""
    assert isinstance(cli, FlaskGroup)
