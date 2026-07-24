def validate_agent(name: str, brokerage_rate: float) -> None:
    if not name or not name.strip():
        raise ValueError("Agent name is required")
    if brokerage_rate is None or brokerage_rate < 0:
        raise ValueError("Brokerage rate must be zero or positive")