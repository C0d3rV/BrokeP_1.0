from dataclasses import dataclass

@dataclass
class Trade:
    trade_id: int
    client_id: int
    segment: str
    symbol: str
    quantity: int
    entry_date: str
    entry_price: float
    entry_brokerage: float
    status: str
    exit_date: str
    exit_price: float
    exit_brokerage: float
    service_fee: float
    gross_pl: float
    net_pl: float
    remarks: str