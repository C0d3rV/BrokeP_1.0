from dataclasses import dataclass


@dataclass
class DailyMark:
    mark_id: int
    trade_id: int
    mark_date: str
    closing_price: float
    unrealized_gross_pl: float
    unrealized_net_pl: float