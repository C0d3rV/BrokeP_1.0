VALID_SEGMENTS = {"EQUITY", "FNO", "COMMODITY"}

def validate_trade_entry(client_id: int, agent_id: int, segment: str,
                          symbol: str, quantity: int, entry_price: float,
                          entry_date: str) -> None:
    if client_id is None:
        raise ValueError("client_id is required")
    if agent_id is None:
        raise ValueError("agent_id is required")
    if segment not in VALID_SEGMENTS:
        raise ValueError(f"segment must be one of {VALID_SEGMENTS}, got '{segment}'")
    if not symbol or not symbol.strip():
        raise ValueError("symbol is required")
    if quantity is None or quantity <= 0:
        raise ValueError("quantity must be greater than 0")
    if entry_price is None or entry_price <= 0:
        raise ValueError("entry_price must be greater than 0")
    if not entry_date:
        raise ValueError("entry_date is required")

def validate_trade_close(exit_price: float, exit_date: str) -> None:
    if exit_price is None or exit_price <= 0:
        raise ValueError("exit_price must be greater than 0")
    if not exit_date:
        raise ValueError("exit_date is required")