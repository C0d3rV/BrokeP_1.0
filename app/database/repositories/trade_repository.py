from app.database.connection import create_connection
from app.domain.entities.trade import Trade


def _row_to_trade(row) -> Trade:
    return Trade(*row)


def open_trade(client_id: int, agent_id: int, segment: str, symbol: str,
               quantity: int, entry_date: str, entry_price: float,
               entry_brokerage: float, entry_service_fee: float = 0,
               expiry_date: str = None, remarks: str = None) -> int:
    con, cursor = create_connection()
    try:
        cursor.execute(
            """INSERT INTO trades (
                   client_id, agent_id, segment, symbol, quantity, expiry_date,
                   entry_date, entry_price, entry_brokerage, entry_service_fee,
                   status, remarks
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?)""",
            (client_id, agent_id, segment, symbol, quantity, expiry_date, entry_date,
             entry_price, entry_brokerage, entry_service_fee, remarks)
        )
        con.commit()
        return cursor.lastrowid
    finally:
        con.close()


def close_trade(trade_id: int, exit_date: str, exit_price: float,
                 exit_brokerage: float, exit_service_fee: float,
                 gross_pl: float, net_pl: float) -> None:
    con, cursor = create_connection()
    try:
        cursor.execute(
            """UPDATE trades
               SET exit_date = ?, exit_price = ?, exit_brokerage = ?,
                   exit_service_fee = ?, gross_pl = ?, net_pl = ?, status = 'CLOSED'
               WHERE trade_id = ? AND status = 'OPEN'""",
            (exit_date, exit_price, exit_brokerage, exit_service_fee,
             gross_pl, net_pl, trade_id)
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Trade {trade_id} not found or already closed")
        con.commit()
    finally:
        con.close()


def get_trade_by_id(trade_id: int) -> Trade | None:
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM trades WHERE trade_id = ?", (trade_id,))
        row = cursor.fetchone()
        return _row_to_trade(row) if row else None
    finally:
        con.close()


def get_open_trades_for_client(client_id: int) -> list[Trade]:
    con, cursor = create_connection()
    try:
        cursor.execute(
            "SELECT * FROM trades WHERE client_id = ? AND status = 'OPEN' ORDER BY entry_date",
            (client_id,)
        )
        return [_row_to_trade(r) for r in cursor.fetchall()]
    finally:
        con.close()


def get_closed_trades_for_client(client_id: int) -> list[Trade]:
    con, cursor = create_connection()
    try:
        cursor.execute(
            "SELECT * FROM trades WHERE client_id = ? AND status = 'CLOSED' ORDER BY exit_date",
            (client_id,)
        )
        return [_row_to_trade(r) for r in cursor.fetchall()]
    finally:
        con.close()


def get_all_open_trades() -> list[Trade]:
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM trades WHERE status = 'OPEN' ORDER BY entry_date")
        return [_row_to_trade(r) for r in cursor.fetchall()]
    finally:
        con.close()


def get_all_closed_trades() -> list[Trade]:
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM trades WHERE status = 'CLOSED' ORDER BY exit_date")
        return [_row_to_trade(r) for r in cursor.fetchall()]
    finally:
        con.close()