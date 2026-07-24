from database.repositories import cash_repository, client_repository
from domain.validators.cash_validator import validate_cash_transaction


def _record(client_id: int, txn_date: str, txn_type: str, amount: float, remarks: str = None) -> int:
    validate_cash_transaction(client_id, txn_type, amount, txn_date)
    if client_repository.get_client_by_id(client_id) is None:
        raise ValueError(f"Client {client_id} does not exist")
    return cash_repository.insert_cash_transaction(client_id, txn_date, txn_type, amount, remarks)


def deposit(client_id: int, txn_date: str, amount: float, remarks: str = None) -> int:
    """FR-11"""
    return _record(client_id, txn_date, "DEPOSIT", amount, remarks)


def withdraw(client_id: int, txn_date: str, amount: float, remarks: str = None) -> int:
    """FR-12"""
    return _record(client_id, txn_date, "WITHDRAWAL", amount, remarks)


def adjust(client_id: int, txn_date: str, amount: float, remarks: str = None) -> int:
    """FR-12"""
    return _record(client_id, txn_date, "ADJUSTMENT", amount, remarks)


def get_ledger_for_client(client_id: int):
    return cash_repository.get_cash_ledger_for_client(client_id)