# tests/cli/test_main.py
# Tests for CLI main entry point and command registration.

from typer.testing import CliRunner

from manchego.cli.main import app


def test_main_callback__shows_help_message():
    """Verify main callback shows help when no subcommand is provided (no_args_is_help=True)."""
    runner = CliRunner()
    result = runner.invoke(app, [])
    
    # With no_args_is_help=True, Typer shows help and exits with code 2
    assert result.exit_code == 2
    assert "Data management system to help track my time and money" in result.output
    assert "version" in result.output


def test_version__outputs_correct_version():
    """Verify version command outputs correct version string."""
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    
    assert result.exit_code == 0
    assert result.output.strip() == "manchego 0.1.0"


def test_help__shows_usage_info():
    """Verify --help flag shows usage information and description."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    
    assert result.exit_code == 0
    assert "Data management system to help track my time and money" in result.output
    # Rich formatting uses box drawing characters, check for "Commands" text
    assert "Commands" in result.output
    assert "version" in result.output


def test_version_command_registered():
    """Verify version command is registered and can be invoked successfully."""
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    
    assert result.exit_code == 0
    assert "manchego 0.1.0" in result.output

