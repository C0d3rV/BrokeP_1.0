from dataclasses import dataclass

@dataclass
class Cash:
    txn_id: int
    client_id: int
    txn_date: str
    txn_type: str
    amount: float
    remarks: str