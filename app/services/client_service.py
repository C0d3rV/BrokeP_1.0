from database.repositories import client_repository
from domain.validators.client_validator import validate_client

def create_client(name: str) -> int:
    validate_client(name)
    return client_repository.insert_client(name)

def get_client(client_id: int):
    client = client_repository.get_client_by_id(client_id)
    if client is None:
        raise ValueError(f"Client {client_id} does not exist")
    return client

def list_clients():
    return client_repository.get_all_clients()

def search_clients(query: str):
    return client_repository.search_clients_by_name(query)