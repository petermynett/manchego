"""Tests for global configuration module."""

import importlib
import warnings
from pathlib import Path

import pytest

import manchego.global_config as gc


def test_project_root_is_absolute():
    """Verify PROJECT_ROOT is an absolute path."""
    assert gc.PROJECT_ROOT.is_absolute()
    assert gc.PROJECT_ROOT.exists()


def test_path_constants_are_path_objects():
    """Verify all root path constants are Path objects."""
    assert isinstance(gc.DATA_ROOT, Path)
    assert isinstance(gc.DB_ROOT, Path)
    assert isinstance(gc.DATASETS_ROOT, Path)
    assert isinstance(gc.LOGS_ROOT, Path)
    assert isinstance(gc.SQL_ROOT, Path)


def test_path_relationships():
    """Verify path relationships are correct."""
    assert gc.DATASETS_ROOT == gc.DATA_ROOT / "datasets"
    assert gc.LOGS_ROOT == gc.DATA_ROOT / "logs"
    assert gc.SCHEMA_PATH == gc.SQL_ROOT / "schema.sql"


@pytest.mark.parametrize("env", ["dev", "stage", "prod"], ids=["dev", "stage", "prod"])
def test_database_paths_for_valid_environments(monkeypatch, env):
    """Verify database paths are correct for each valid environment."""
    monkeypatch.setenv("MANCHEGO_ENV", env)
    importlib.reload(gc)

    assert gc.DB_PATHS[env] == Path("db") / f"manchego_{env}.db"
    assert gc.DB_PATHS[env] == gc.DATABASE_PATH
    assert env == gc.MANCHEGO_ENV


@pytest.mark.parametrize("env", ["dev", "stage", "prod"], ids=["dev", "stage", "prod"])
def test_snapshot_directories_for_environments(monkeypatch, env):
    """Verify snapshot directories are correct for each environment."""
    monkeypatch.setenv("MANCHEGO_ENV", env)
    importlib.reload(gc)

    assert gc.DB_SNAPSHOT_DIRS[env] == Path("db") / "snapshots" / env
    assert gc.DB_SNAPSHOT_DIRS[env] == gc.DB_SNAPSHOT_DIR


def test_invalid_environment_defaults_to_dev(monkeypatch):
    """Verify invalid environment defaults to dev with warning."""
    monkeypatch.setenv("MANCHEGO_ENV", "invalid_env")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        importlib.reload(gc)
        assert len(w) > 0
        assert "Invalid MANCHEGO_ENV" in str(w[0].message)

    assert gc.MANCHEGO_ENV == "dev"
    assert gc.DB_PATHS["dev"] == gc.DATABASE_PATH


def test_api_keys_read_from_environment(monkeypatch):
    """Verify API keys are read from environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", "/path/to/credentials.json")
    importlib.reload(gc)

    assert gc.OPENAI_API_KEY == "test_openai_key"
    assert gc.GOOGLE_CREDENTIALS_PATH == "/path/to/credentials.json"


def test_missing_openai_api_key_warns(monkeypatch):
    """Verify warning is emitted when OPENAI_API_KEY is not set."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        importlib.reload(gc)
        warning_messages = [str(warning.message) for warning in w]
        assert any("OPENAI_API_KEY not set" in msg for msg in warning_messages)


def test_missing_google_credentials_path_warns(monkeypatch):
    """Verify warning is emitted when GOOGLE_CREDENTIALS_PATH is not set."""
    monkeypatch.delenv("GOOGLE_CREDENTIALS_PATH", raising=False)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        importlib.reload(gc)
        warning_messages = [str(warning.message) for warning in w]
        assert any("GOOGLE_CREDENTIALS_PATH not set" in msg for msg in warning_messages)


def test_get_log_path__simple_module():
    """Verify get_log_path handles simple module names."""
    result = gc.get_log_path("receipts")
    assert result == Path("data/logs/receipts/receipts.log")


def test_get_log_path__nested_module():
    """Verify get_log_path handles nested module names."""
    result = gc.get_log_path("receipts.preprocess")
    assert result == Path("data/logs/receipts/preprocess.log")


def test_get_log_path__deeply_nested_module():
    """Verify get_log_path handles deeply nested module names."""
    result = gc.get_log_path("receipts.preprocess.transform")
    assert result == Path("data/logs/receipts/transform.log")


@pytest.mark.parametrize(
    "module_name,expected_path",
    [
        ("ledger", Path("data/logs/ledger/ledger.log")),
        ("time", Path("data/logs/time/time.log")),
        ("time.rescuetime", Path("data/logs/time/rescuetime.log")),
        ("receipts.intake", Path("data/logs/receipts/intake.log")),
    ],
    ids=["ledger", "time", "time.rescuetime", "receipts.intake"],
)
def test_get_log_path__various_modules(module_name, expected_path):
    """Verify get_log_path handles various module name formats."""
    result = gc.get_log_path(module_name)
    assert result == expected_path


def test_get_log_path__domain_extraction():
    """Verify get_log_path extracts domain correctly (first part)."""
    result = gc.get_log_path("receipts.preprocess")
    # Domain should be "receipts" (first part)
    assert result.parent.name == "receipts"


def test_get_log_path__filename_extraction():
    """Verify get_log_path extracts filename correctly (last part)."""
    result = gc.get_log_path("receipts.preprocess.transform")
    # Filename should be "transform.log" (last part)
    assert result.name == "transform.log"
