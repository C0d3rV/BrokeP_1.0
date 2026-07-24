VALID_TXN_TYPES = {"DEPOSIT", "WITHDRAWAL", "ADJUSTMENT"}

def validate_cash_transaction(client_id: int, txn_type: str, amount: float, txn_date: str) -> None:
    if client_id is None:
        raise ValueError("client_id is required")
    if txn_type not in VALID_TXN_TYPES:
        raise ValueError(f"txn_type must be one of {VALID_TXN_TYPES}, got '{txn_type}'")
    if amount is None or amount <= 0:
        raise ValueError("amount must be greater than 0 (sign is handled by txn_type)")
    if not txn_date:
        raise ValueError("txn_date is required")