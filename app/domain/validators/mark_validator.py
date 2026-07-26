def validate_mark(closing_price: float, mark_date: str) -> None:
    if closing_price is None or closing_price <= 0:
        raise ValueError("Closing price must be greater than 0")
    if not mark_date:
        raise ValueError("mark_date is required")