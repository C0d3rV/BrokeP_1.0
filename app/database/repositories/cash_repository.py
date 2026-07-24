from app.database.connection import create_connection
from app.domain.entities.cash import Cash

def _row_to_cash_txn(row) -> Cash:
    return Cash(*row)

def insert_cash_transaction(client_id: int, txn_date: str, txn_type: str,
                             amount: float, remarks: str = None) -> int:
    """txn_type: 'DEPOSIT' / 'WITHDRAWAL' / 'ADJUSTMENT'.
    amount is always stored positive — sign/direction is derived from txn_type
    at calculation time (domain/calculations.running_balance), not here."""
    con, cursor = create_connection()
    try:
        cursor.execute(
            """INSERT INTO cash_transactions (client_id, txn_date, txn_type, amount, remarks)
               VALUES (?, ?, ?, ?, ?)""",
            (client_id, txn_date, txn_type, amount, remarks)
        )
        con.commit()
        return cursor.lastrowid
    finally:
        con.close()

def get_cash_ledger_for_client(client_id: int) -> list[Cash]:
    con, cursor = create_connection()
    try:
        cursor.execute(
            "SELECT * FROM cash_transactions WHERE client_id = ? ORDER BY txn_date",
            (client_id,)
        )
        return [_row_to_cash_txn(r) for r in cursor.fetchall()]
    finally:
        con.close()