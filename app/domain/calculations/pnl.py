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