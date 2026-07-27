import pytest
from app.services import cash_service
from app.database.repositories import client_repository


@pytest.fixture
def client(test_db):
    return client_repository.insert_client("Kailash")


def test_deposit(client):
    cash_service.deposit(client, "2026-06-01", 500000)
    ledger = cash_service.get_ledger_for_client(client)
    assert ledger[0].txn_type == "DEPOSIT"
    assert ledger[0].amount == 500000


def test_withdraw(client):
    cash_service.withdraw(client, "2026-06-05", 10000)
    ledger = cash_service.get_ledger_for_client(client)
    assert ledger[0].txn_type == "WITHDRAWAL"


def test_deposit_invalid_client_raises():
    import pytest as _pytest
    # deliberately no test_db fixture used directly here -- rely on client fixture instead
    pass  # placeholder removed below


def test_deposit_zero_amount_raises(client):
    with pytest.raises(ValueError):
        cash_service.deposit(client, "2026-06-01", 0)


def test_deposit_nonexistent_client_raises(test_db):
    with pytest.raises(ValueError):
        cash_service.deposit(9999, "2026-06-01", 500000)