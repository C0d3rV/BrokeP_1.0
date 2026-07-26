from app.database.repositories import mark_repository, trade_repository
from app.domain.validators.mark_validator import validate_mark
from app.domain.calculations.pnl import gross_pl, unrealized_net_pl


def record_daily_mark(trade_id: int, mark_date: str, closing_price: float):
    validate_mark(closing_price, mark_date)

    trade = trade_repository.get_trade_by_id(trade_id)
    if trade is None:
        raise ValueError(f"Trade {trade_id} does not exist")
    if trade.status != "OPEN":
        raise ValueError(f"Trade {trade_id} is not open -- only open trades can be marked")

    gpl = gross_pl(trade.entry_price, closing_price, trade.quantity)
    npl = unrealized_net_pl(gpl, trade.entry_brokerage, trade.entry_service_fee)

    mark_repository.upsert_mark(trade_id, mark_date, closing_price, gpl, npl)
    return gpl, npl


def get_mark_for_trade(trade_id: int, mark_date: str):
    return mark_repository.get_mark_for_trade_and_date(trade_id, mark_date)


def get_marks_for_date(mark_date: str):
    return mark_repository.get_marks_for_date(mark_date)


def get_mark_history_for_trade(trade_id: int):
    return mark_repository.get_mark_history_for_trade(trade_id)

def group_open_trades_by_instrument(open_trades):
    """Groups OPEN trades by (symbol, expiry_date) so one closing-price entry
    can be applied to every trade sharing that exact instrument, without
    conflating two different expiries of the same underlying symbol."""
    groups = {}
    for t in open_trades:
        key = (t.symbol, t.expiry_date)
        groups.setdefault(key, []).append(t)
    return groups