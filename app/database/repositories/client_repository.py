from app.database.connection import create_connection
from app.domain.entities.client import Client
from datetime import datetime, timezone

def _row_to_client(row) -> Client:
    return Client(*row)

def insert_client(name: str) -> int:
    """Returns the new client_id."""
    con, cursor = create_connection()
    try:
        cursor.execute(
            "INSERT INTO clients (name, created_at) VALUES (?, ?)",
            (name, datetime.now(timezone.utc).isoformat())
        )
        con.commit()
        return cursor.lastrowid
    finally:
        con.close()

def get_client_by_id(client_id: int) -> Client | None:
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()
        return _row_to_client(row) if row else None
    finally:
        con.close()

def get_all_clients() -> list[Client]:
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM clients ORDER BY name")
        return [_row_to_client(r) for r in cursor.fetchall()]
    finally:
        con.close()

def search_clients_by_name(query: str) -> list[Client]:
    con, cursor = create_connection()
    try:
        cursor.execute(
            "SELECT * FROM clients WHERE name LIKE ? ORDER BY name",
            (f"%{query}%",)
        )
        return [_row_to_client(r) for r in cursor.fetchall()]
    finally:
        con.close()