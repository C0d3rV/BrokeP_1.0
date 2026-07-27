import pytest
from app.domain.calculations.pnl import gross_value, brokerage, gross_pl, net_pl, running_balance


class TestGrossValue:
    def test_basic(self):
        assert gross_value(100, 50) == 5000

    def test_zero_quantity(self):
        assert gross_value(100, 0) == 0


class TestBrokerage:
    def test_rate_based(self):
        # buy 1000 + sell 1000 = 2000 turnover, 0.035% rate
        assert brokerage(buy_value=1000, sell_value=1000, rate=0.035) == 0.70

    def test_manual_override_takes_priority(self):
        assert brokerage(buy_value=1000, sell_value=1000, rate=0.035, manual_override=50) == 50

    def test_raises_if_neither_given(self):
        with pytest.raises(ValueError):
            brokerage(buy_value=1000, sell_value=1000)

    def test_single_leg(self):
        # entry-only, sell_value=0
        assert brokerage(buy_value=981200, sell_value=0, rate=0.035) == 343.42


class TestGrossPL:
    def test_profit(self):
        assert gross_pl(entry_price=1214, exit_price=1239, quantity=400) == 10000

    def test_loss(self):
        assert gross_pl(entry_price=2926, exit_price=2830, quantity=625) == -60000

    def test_flat(self):
        assert gross_pl(entry_price=100, exit_price=100, quantity=10) == 0


class TestNetPL:
    def test_basic(self):
        # gross 10000, entry_brok 200, exit_brok 200, service_fee 50
        assert net_pl(10000, 200, 200, 50) == 9550

    def test_default_service_fee(self):
        assert net_pl(10000, 200, 200) == 9600


class TestRunningBalance:
    def test_deposit_only(self):
        assert running_balance(previous=0, deposits=500000, withdrawals=0, net_pl_val=0) == 500000

    def test_full_formula(self):
        result = running_balance(previous=500000, deposits=200000,
                                  withdrawals=10000, net_pl_val=39407.098, adjustments=0)
        assert result == pytest.approx(729407.098)