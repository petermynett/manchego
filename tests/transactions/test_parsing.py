"""Tests for CSV parsing and transformation."""

import pytest

from manchego.transactions import config, parsing


class TestParseRow:
    """Test single row parsing."""

    def test_parse_valid_4_column_row(self):
        """Parses valid 4-column row (chequing/savings format)."""
        row = ["2025-01-15", "Test Transaction", "10.50", ""]
        result = parsing.parse_row(row, 1)

        assert result is not None
        assert result["transaction_date"] == "2025-01-15"
        assert result["description"] == "Test Transaction"
        assert result["amount"] == -10.50  # Debit is negative
        assert result["currency"] == "CAD"
        assert "id" in result

    def test_parse_valid_5_column_row(self):
        """Parses valid 5-column row (credit card format)."""
        row = ["2025-01-15", "Test Transaction", "10.50", "", "4500********9256"]
        result = parsing.parse_row(row, 1)

        assert result is not None
        assert result["transaction_date"] == "2025-01-15"
        assert result["description"] == "Test Transaction"
        assert result["amount"] == -10.50  # Debit is negative
        assert result["currency"] == "CAD"

    def test_parse_credit_amount(self):
        """Parses credit amount as positive."""
        row = ["2025-01-15", "Deposit", "", "100.00"]
        result = parsing.parse_row(row, 1)

        assert result is not None
        assert result["amount"] == 100.00  # Credit is positive

    def test_parse_missing_date(self):
        """Raises ParseError for missing date."""
        row = ["", "Test Transaction", "10.50", ""]

        with pytest.raises(parsing.ParseError, match="Missing transaction date"):
            parsing.parse_row(row, 1)

    def test_parse_invalid_date_format(self):
        """Raises ParseError for invalid date format."""
        row = ["01/15/2025", "Test Transaction", "10.50", ""]

        with pytest.raises(parsing.ParseError, match="Invalid date format"):
            parsing.parse_row(row, 1)

    def test_parse_missing_description(self):
        """Raises ParseError for missing description."""
        row = ["2025-01-15", "", "10.50", ""]

        with pytest.raises(parsing.ParseError, match="Missing description"):
            parsing.parse_row(row, 1)

    def test_parse_missing_amounts(self):
        """Raises ParseError when both debit and credit are missing."""
        row = ["2025-01-15", "Test Transaction", "", ""]

        with pytest.raises(
            parsing.ParseError, match="Missing both debit and credit amounts"
        ):
            parsing.parse_row(row, 1)

    def test_parse_invalid_amount(self):
        """Raises ParseError for invalid amount."""
        row = ["2025-01-15", "Test Transaction", "invalid", ""]

        with pytest.raises(parsing.ParseError, match="Invalid amount"):
            parsing.parse_row(row, 1)

    def test_parse_too_few_columns(self):
        """Raises ParseError for too few columns."""
        row = ["2025-01-15", "Test Transaction"]

        with pytest.raises(parsing.ParseError, match="expected at least 4"):
            parsing.parse_row(row, 1)


class TestParseTransactionFile:
    """Test file parsing."""

    def test_parse_valid_file(self, tmp_path):
        """Parses valid transaction file."""
        file = config.TRANSACTIONS_RAW_DIR / "test.csv"
        file.write_text(
            "2025-01-15,Transaction 1,10.50,\n2025-01-16,Transaction 2,,20.75\n"
        )

        rows, errors, min_date, max_date = parsing.parse_transaction_file(file)

        assert len(rows) == 2
        assert len(errors) == 0
        assert min_date == "2025-01-15"
        assert max_date == "2025-01-16"
        assert rows[0]["amount"] == -10.50
        assert rows[1]["amount"] == 20.75

    def test_parse_file_with_errors(self, tmp_path):
        """Collects parsing errors and continues processing."""
        file = config.TRANSACTIONS_RAW_DIR / "test.csv"
        file.write_text(
            "2025-01-15,Valid Transaction,10.50,\n"
            "invalid-date,Invalid Transaction,10.50,\n"
            "2025-01-16,Another Valid Transaction,,20.75\n"
        )

        rows, errors, min_date, max_date = parsing.parse_transaction_file(file)

        assert len(rows) == 2  # Two valid rows
        assert len(errors) == 1  # One error
        assert min_date == "2025-01-15"
        assert max_date == "2025-01-16"

    def test_parse_empty_file(self, tmp_path):
        """Handles empty file gracefully."""
        file = config.TRANSACTIONS_RAW_DIR / "empty.csv"
        file.write_text("")

        rows, errors, min_date, max_date = parsing.parse_transaction_file(file)

        assert len(rows) == 0
        assert len(errors) == 0
        assert min_date is None
        assert max_date is None

    def test_parse_file_with_empty_rows(self, tmp_path):
        """Skips empty rows."""
        file = config.TRANSACTIONS_RAW_DIR / "test.csv"
        file.write_text(
            "2025-01-15,Transaction 1,10.50,\n\n2025-01-16,Transaction 2,,20.75\n"
        )

        rows, errors, _min_date, _max_date = parsing.parse_transaction_file(file)

        assert len(rows) == 2
        assert len(errors) == 0
