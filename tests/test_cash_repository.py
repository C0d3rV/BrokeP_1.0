import pytest
from app.database.repositories import cash_repository, client_repository


@pytest.fixture
def client(test_db):
    return client_repository.insert_client("Kailash")


def test_insert_and_get_ledger(client):
    cash_repository.insert_cash_transaction(client, "2026-06-01", "DEPOSIT", 500000)
    cash_repository.insert_cash_transaction(client, "2026-06-02", "DEPOSIT", 200000)

    ledger = cash_repository.get_cash_ledger_for_client(client)
    assert len(ledger) == 2
    assert ledger[0].amount == 500000
    assert ledger[0].txn_type == "DEPOSIT"


def test_withdrawal_stored_positive_with_type(client):
    cash_repository.insert_cash_transaction(client, "2026-06-05", "WITHDRAWAL", 10000)

    ledger = cash_repository.get_cash_ledger_for_client(client)
    assert ledger[0].amount == 10000
    assert ledger[0].txn_type == "WITHDRAWAL"


def test_ledger_ordered_by_date(client):
    cash_repository.insert_cash_transaction(client, "2026-06-10", "DEPOSIT", 1000)
    cash_repository.insert_cash_transaction(client, "2026-06-01", "DEPOSIT", 2000)

    ledger = cash_repository.get_cash_ledger_for_client(client)
    assert ledger[0].txn_date == "2026-06-01"
    assert ledger[1].txn_date == "2026-06-10"