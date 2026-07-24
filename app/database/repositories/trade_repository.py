from database.connection import create_connection
from domain.entities.trade import Trade

def _row_to_trade(row) -> Trade:
    return Trade(*row)

def open_trade(client_id: int, agent_id: int, segment: str, symbol: str, quantity: int,
               entry_date: str, entry_price: float, entry_brokerage: float,
               remarks: str = None) -> int:
    """Inserts a new OPEN trade. Returns the new trade_id.
    Gross value / brokerage math happens in domain/calculations before this is called —
    this function just writes what it's given."""
    con, cursor = create_connection()
    try:
        cursor.execute(
            """INSERT INTO trades (
                   client_id, agent_id, segment, symbol, quantity,
                   entry_date, entry_price, entry_brokerage, status, remarks
               ) VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?)""",
            (client_id, agent_id, segment, symbol, quantity, entry_date,
             entry_price, entry_brokerage, remarks)
        )
        con.commit()
        return cursor.lastrowid
    finally:
        con.close()

def close_trade(trade_id: int, exit_date: str, exit_price: float,
                 exit_brokerage: float, service_fee: float,
                 gross_pl: float, net_pl: float) -> None:
    """Writes the close in one atomic UPDATE. gross_pl/net_pl must already be
    computed by domain/calculations and passed in — this function does not
    calculate anything, only persists. Only ever targets a row where
    status='OPEN', enforcing 'never re-open a CLOSED trade' at the SQL level."""
    con, cursor = create_connection()
    try:
        cursor.execute(
            """UPDATE trades
               SET exit_date = ?, exit_price = ?, exit_brokerage = ?,
                   service_fee = ?, gross_pl = ?, net_pl = ?, status = 'CLOSED'
               WHERE trade_id = ? AND status = 'OPEN'""",
            (exit_date, exit_price, exit_brokerage, service_fee,
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
    """FR-14"""
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM trades WHERE status = 'OPEN' ORDER BY entry_date")
        return [_row_to_trade(r) for r in cursor.fetchall()]
    finally:
        con.close()

def get_all_closed_trades() -> list[Trade]:
    """FR-15"""
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM trades WHERE status = 'CLOSED' ORDER BY exit_date")
        return [_row_to_trade(r) for r in cursor.fetchall()]
    finally:
        con.close()