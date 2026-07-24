def validate_client(name: str) -> None:
    if not name or not name.strip():
        raise ValueError("Client name is required")