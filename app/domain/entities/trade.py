from dataclasses import dataclass
from typing import Optional

@dataclass
class Trade:
    trade_id: int
    client_id: int
    agent_id: int
    segment: str
    symbol: str
    quantity: int
    entry_date: str
    entry_price: float
    entry_brokerage: float
    entry_service_fee: float
    status: str
    exit_date: Optional[str]
    exit_price: Optional[float]
    exit_brokerage: Optional[float]
    exit_service_fee: Optional[float]
    gross_pl: Optional[float]
    net_pl: Optional[float]
    expiry_date: Optional[str]
    remarks: Optional[str]