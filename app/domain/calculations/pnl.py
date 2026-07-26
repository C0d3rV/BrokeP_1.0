# domain/calculations/pnl.py

def gross_value(price: float, quantity: int) -> float:
    """FR-04"""
    return price * quantity


def brokerage(buy_value: float, sell_value: float,
              rate: float = None, manual_override: float = None) -> float:
    """
    rate: brokerage rate as a PERCENTAGE (e.g. 0.035 for 0.035%), applied to
          combined buy+sell turnover. Internally divided by 100.
          Caller (service layer) is responsible for knowing which agent's
          rate applies to this trade.
    manual_override: if given, bypasses rate entirely and returns this value
          as-is. Takes priority over rate.
    Exactly one of rate or manual_override must be provided.
    """
    if manual_override is not None:
        return round(manual_override, 2)
    if rate is None:
        raise ValueError("Either rate or manual_override must be provided")
    return round((buy_value + sell_value) * (rate / 100), 2)


def gross_pl(entry_price: float, exit_price: float, quantity: int) -> float:
    """FR-08"""
    return (exit_price - entry_price) * quantity


def net_pl(gross_pl_val: float, entry_brokerage: float, exit_brokerage: float,
           entry_service_fee: float = 0, exit_service_fee: float = 0) -> float:
    """FR-09"""
    return gross_pl_val - entry_brokerage - exit_brokerage - entry_service_fee - exit_service_fee


def running_balance(previous: float, deposits: float, withdrawals: float,
                     net_pl_val: float, adjustments: float = 0) -> float:
    """§6"""
    return previous + deposits - withdrawals + net_pl_val + adjustments


def unrealized_net_pl(gross_pl_val: float, entry_brokerage: float, entry_service_fee: float = 0) -> float:
    """Mark-to-market P&L for a still-OPEN trade -- only costs actually
    incurred so far (entry side) are deducted. Exit costs don't exist yet,
    so they are never estimated or guessed at here."""
    return gross_pl_val - entry_brokerage - entry_service_fee