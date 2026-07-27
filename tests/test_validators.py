import pytest
from app.domain.validators.client_validator import validate_client
from app.domain.validators.agent_validator import validate_agent
from app.domain.validators.trade_validator import validate_trade_entry, validate_trade_close
from app.domain.validators.cash_validator import validate_cash_transaction


class TestClientValidator:
    def test_valid_name_passes(self):
        validate_client("Kailash")  # should not raise

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            validate_client("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            validate_client("   ")


class TestAgentValidator:
    def test_valid_passes(self):
        validate_agent("Gagan", 0.035)

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError):
            validate_agent("Gagan", -0.01)

    def test_zero_rate_allowed(self):
        validate_agent("Gagan", 0)  # zero rate is valid, per spec


class TestTradeValidator:
    def test_valid_entry_passes(self):
        validate_trade_entry(1, 1, "EQUITY", "INFY", 400, 1214, "2026-06-01")

    def test_invalid_segment_raises(self):
        with pytest.raises(ValueError):
            validate_trade_entry(1, 1, "CRYPTO", "INFY", 400, 1214, "2026-06-01")

    def test_zero_quantity_raises(self):
        with pytest.raises(ValueError):
            validate_trade_entry(1, 1, "EQUITY", "INFY", 0, 1214, "2026-06-01")

    def test_negative_price_raises(self):
        with pytest.raises(ValueError):
            validate_trade_entry(1, 1, "EQUITY", "INFY", 400, -5, "2026-06-01")

    def test_missing_client_id_raises(self):
        with pytest.raises(ValueError):
            validate_trade_entry(None, 1, "EQUITY", "INFY", 400, 1214, "2026-06-01")

    def test_close_valid_passes(self):
        validate_trade_close(1239, "2026-06-02")

    def test_close_zero_price_raises(self):
        with pytest.raises(ValueError):
            validate_trade_close(0, "2026-06-02")


class TestCashValidator:
    def test_valid_deposit_passes(self):
        validate_cash_transaction(1, "DEPOSIT", 500000, "2026-06-01")

    def test_invalid_txn_type_raises(self):
        with pytest.raises(ValueError):
            validate_cash_transaction(1, "BONUS", 500, "2026-06-01")

    def test_zero_amount_raises(self):
        with pytest.raises(ValueError):
            validate_cash_transaction(1, "DEPOSIT", 0, "2026-06-01")