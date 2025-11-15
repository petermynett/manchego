"""Shared fixtures for transaction tests."""

import pytest

from manchego.transactions import config, discovery


@pytest.fixture(autouse=True)
def _redirect_transaction_dirs(tmp_path, monkeypatch):
    """Redirect transaction directories to tmp_path for test isolation.

    Redirects:
    - TRANSACTIONS_RAW_DIR (input)
    - TRANSACTIONS_BACKUP_RAW_DIR (output)
    - TRANSACTIONS_IMPORTED_DIR (output)
    """
    raw_dir = tmp_path / "transactions" / "raw"
    backup_dir = tmp_path / "transactions" / "backup_raw"
    imported_dir = tmp_path / "transactions" / "imported"

    raw_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)
    imported_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(config, "TRANSACTIONS_RAW_DIR", raw_dir)
    monkeypatch.setattr(config, "TRANSACTIONS_BACKUP_RAW_DIR", backup_dir)
    monkeypatch.setattr(config, "TRANSACTIONS_IMPORTED_DIR", imported_dir)
    # Also patch in discovery module since it imports at module level
    monkeypatch.setattr(discovery, "TRANSACTIONS_RAW_DIR", raw_dir)

    return {"raw": raw_dir, "backup": backup_dir, "imported": imported_dir}
