"""Tests for account identification logic."""

import pytest

from manchego.transactions import config, identification


class TestIdentifyAccount:
    """Test account identification functionality."""

    def test_filename_override_personal_visa(self, tmp_path):
        """Identifies personal-visa from filename."""
        file = config.TRANSACTIONS_RAW_DIR / "personal-visa_statement.csv"
        file.write_text("2025-01-01,Test,10.00,,\n")

        result = identification.identify_account(file)

        assert result == "personal-visa"

    def test_filename_override_visa_personal(self, tmp_path):
        """Identifies personal-visa from visa-personal in filename."""
        file = config.TRANSACTIONS_RAW_DIR / "visa-personal_statement.csv"
        file.write_text("2025-01-01,Test,10.00,,\n")

        result = identification.identify_account(file)

        assert result == "personal-visa"

    def test_filename_override_business_visa(self, tmp_path):
        """Identifies business-visa from filename."""
        file = config.TRANSACTIONS_RAW_DIR / "business-visa_statement.csv"
        file.write_text("2025-01-01,Test,10.00,,\n")

        result = identification.identify_account(file)

        assert result == "business-visa"

    def test_card_number_9256(self, tmp_path):
        """Identifies personal-visa from card number ending in 9256."""
        file = config.TRANSACTIONS_RAW_DIR / "statement.csv"
        file.write_text("2025-01-01,Test,10.00,,4500********9256\n")

        result = identification.identify_account(file)

        assert result == "personal-visa"

    def test_card_number_4128(self, tmp_path):
        """Identifies business-visa from card number ending in 4128."""
        file = config.TRANSACTIONS_RAW_DIR / "statement.csv"
        file.write_text("2025-01-01,Test,10.00,,4500********4128\n")

        result = identification.identify_account(file)

        assert result == "business-visa"

    def test_suzanne_rent_payment(self, tmp_path):
        """Identifies personal-chequing from Suzanne rent payment."""
        file = config.TRANSACTIONS_RAW_DIR / "statement.csv"
        # Suzanne payment around 1st of month, ~$1200-1250
        file.write_text(
            "2025-01-01,Internet Banking E-TRANSFER 105639704773 Suzanne,1241.15,,\n"
        )

        result = identification.identify_account(file)

        assert result == "personal-chequing"

    def test_socan_payment_no_suzanne(self, tmp_path):
        """Identifies business-savings from SOCAN payment without Suzanne."""
        file = config.TRANSACTIONS_RAW_DIR / "statement.csv"
        file.write_text(
            "2025-01-15,Electronic Funds Transfer PAY 50950570 SOCAN,,3.15,\n"
        )

        result = identification.identify_account(file)

        assert result == "business-savings"

    def test_socan_with_suzanne_not_savings(self, tmp_path):
        """Does not identify as savings if both SOCAN and Suzanne present."""
        file = config.TRANSACTIONS_RAW_DIR / "statement.csv"
        file.write_text(
            "2025-01-01,Internet Banking E-TRANSFER 105639704773 Suzanne,1241.15,,\n"
            "2025-01-15,Electronic Funds Transfer PAY 50950570 SOCAN,,3.15,\n"
        )

        result = identification.identify_account(file)

        # Should identify as personal-chequing (Suzanne takes precedence)
        assert result == "personal-chequing"

    def test_unidentified_file(self, tmp_path):
        """Returns None for unidentified files."""
        file = config.TRANSACTIONS_RAW_DIR / "unknown.csv"
        file.write_text("2025-01-01,Some Transaction,10.00,,\n")

        result = identification.identify_account(file)

        assert result is None

    def test_empty_file(self, tmp_path):
        """Returns None for empty files."""
        file = config.TRANSACTIONS_RAW_DIR / "empty.csv"
        file.write_text("")

        result = identification.identify_account(file)

        assert result is None


class TestGetAccountId:
    """Test account ID lookup."""

    def test_valid_account_labels(self):
        """Returns correct UUID for valid account labels."""
        assert (
            identification.get_account_id("personal-visa")
            == "account-personal-visa-uuid"
        )
        assert (
            identification.get_account_id("business-visa")
            == "account-business-visa-uuid"
        )
        assert (
            identification.get_account_id("personal-chequing")
            == "account-checking-uuid"
        )
        assert (
            identification.get_account_id("business-savings") == "account-savings-uuid"
        )

    def test_invalid_account_label(self):
        """Raises ValueError for invalid account label."""
        with pytest.raises(ValueError, match="Unknown account label"):
            identification.get_account_id("invalid-label")
