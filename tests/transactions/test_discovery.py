"""Tests for transaction file discovery."""

from pathlib import Path

from manchego.transactions import config, discovery


class TestGetRawTransactionFiles:
    """Test file discovery functionality."""

    def test_empty_directory(self):
        """Returns empty list when no files exist."""
        result = discovery.get_raw_transaction_files()
        assert result == []

    def test_with_files(self, tmp_path, touch):
        """Returns matching CSV files."""
        # Create test files
        file1 = config.TRANSACTIONS_RAW_DIR / "test1.csv"
        file2 = config.TRANSACTIONS_RAW_DIR / "test2.csv"
        file1.write_text("data")
        file2.write_text("data")

        result = discovery.get_raw_transaction_files()

        assert len(result) == 2
        assert file1 in result
        assert file2 in result

    def test_filters_non_matching(self, tmp_path, touch):
        """Filters out non-CSV files."""
        csv_file = config.TRANSACTIONS_RAW_DIR / "test.csv"
        txt_file = config.TRANSACTIONS_RAW_DIR / "readme.txt"
        csv_file.write_text("data")
        txt_file.write_text("text")

        result = discovery.get_raw_transaction_files()

        assert len(result) == 1
        assert result[0] == csv_file

    def test_returns_path_objects(self, tmp_path, touch):
        """Returns Path objects, not strings."""
        file = config.TRANSACTIONS_RAW_DIR / "test.csv"
        file.write_text("data")

        result = discovery.get_raw_transaction_files()

        assert len(result) == 1
        assert isinstance(result[0], Path)
