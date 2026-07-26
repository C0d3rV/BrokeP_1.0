from app.database.connection import create_connection
from app.domain.entities.daily_mark import DailyMark


def _row_to_mark(row) -> DailyMark:
    return DailyMark(*row)


def upsert_mark(trade_id: int, mark_date: str, closing_price: float,
                 unrealized_gross_pl: float, unrealized_net_pl: float) -> None:
    con, cursor = create_connection()
    try:
        cursor.execute(
            """INSERT INTO daily_marks (trade_id, mark_date, closing_price,
                                          unrealized_gross_pl, unrealized_net_pl)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(trade_id, mark_date) DO UPDATE SET
                   closing_price = excluded.closing_price,
                   unrealized_gross_pl = excluded.unrealized_gross_pl,
                   unrealized_net_pl = excluded.unrealized_net_pl""",
            (trade_id, mark_date, closing_price, unrealized_gross_pl, unrealized_net_pl)
        )
        con.commit()
    finally:
        con.close()


def get_mark_for_trade_and_date(trade_id: int, mark_date: str) -> DailyMark | None:
    con, cursor = create_connection()
    try:
        cursor.execute(
            "SELECT * FROM daily_marks WHERE trade_id = ? AND mark_date = ?",
            (trade_id, mark_date)
        )
        row = cursor.fetchone()
        return _row_to_mark(row) if row else None
    finally:
        con.close()


def get_marks_for_date(mark_date: str) -> list[DailyMark]:
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM daily_marks WHERE mark_date = ?", (mark_date,))
        return [_row_to_mark(r) for r in cursor.fetchall()]
    finally:
        con.close()


def get_mark_history_for_trade(trade_id: int) -> list[DailyMark]:
    con, cursor = create_connection()
    try:
        cursor.execute(
            "SELECT * FROM daily_marks WHERE trade_id = ? ORDER BY mark_date",
            (trade_id,)
        )
        return [_row_to_mark(r) for r in cursor.fetchall()]
    finally:
        con.close()