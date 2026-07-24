from dataclasses import dataclass

@dataclass
class Client:
    client_id: int
    name: str
    created_at: str