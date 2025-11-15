"""Tests for transaction import functionality."""

from unittest.mock import MagicMock, patch

import pytest

import manchego.transactions.loader as import_module
from manchego.transactions import config


class TestImportSingleFile:
    """Test single file import."""

    @pytest.fixture
    def mock_db(self, tmp_path, monkeypatch):
        """Mock database connection."""
        # Create a mock database path
        db_path = tmp_path / "test.db"
        monkeypatch.setattr(
            "manchego.database.connection.DatabaseConnection", MagicMock
        )
        return db_path

    def test_import_identified_file(self, tmp_path, mock_db):
        """Imports file with identified account."""
        # Create test file with card number
        file = config.TRANSACTIONS_RAW_DIR / "test.csv"
        file.write_text("2025-01-15,Test Transaction,10.50,,4500********9256\n")

        with patch("manchego.transactions.loader.DatabaseConnection") as mock_conn:
            mock_conn.return_value.__enter__.return_value.cursor.return_value.execute = MagicMock()
            mock_conn.return_value.__enter__.return_value.commit = MagicMock()

            result = import_module.import_single_file(file, "test_op_id")

            assert result["success"] is True
            assert result["rows_imported"] == 1

    def test_import_unidentified_file(self, tmp_path):
        """Skips file with unidentified account."""
        file = config.TRANSACTIONS_RAW_DIR / "unknown.csv"
        file.write_text("2025-01-15,Unknown Transaction,10.50,\n")

        result = import_module.import_single_file(file, "test_op_id")

        assert result["success"] is False
        assert result["reason"] == "Account identification failed"
        assert result["rows_imported"] == 0

    def test_import_empty_file(self, tmp_path):
        """Handles empty file."""
        file = config.TRANSACTIONS_RAW_DIR / "empty.csv"
        file.write_text("")

        result = import_module.import_single_file(file, "test_op_id")

        # Should fail because account can't be identified from empty file
        assert result["success"] is False


class TestImportTransactions:
    """Test main import function."""

    def test_import_no_files(self, tmp_path):
        """Handles no files gracefully."""
        result = import_module.import_transactions("test_op_id")

        assert result["success"] is True
        assert result["total"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0

    def test_import_with_files(self, tmp_path):
        """Imports multiple files."""
        # Create test files
        file1 = config.TRANSACTIONS_RAW_DIR / "visa1.csv"
        file1.write_text("2025-01-15,Test Transaction,10.50,,4500********9256\n")

        file2 = config.TRANSACTIONS_RAW_DIR / "visa2.csv"
        file2.write_text("2025-01-16,Another Transaction,20.75,,4500********9256\n")

        with patch("manchego.transactions.loader.DatabaseConnection") as mock_conn:
            mock_conn.return_value.__enter__.return_value.cursor.return_value.execute = MagicMock()
            mock_conn.return_value.__enter__.return_value.commit = MagicMock()

            result = import_module.import_transactions("test_op_id")

            assert result["total"] == 2
            # Files should be processed (success depends on DB mock)
