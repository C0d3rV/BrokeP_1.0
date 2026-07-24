from database.connection import create_connection
from domain.entities.agent import Agent

def _row_to_agent(row) -> Agent:
    return Agent(*row)

def insert_agent(name: str, brokerage_rate: float) -> int:
    """Returns the new agent_id."""
    con, cursor = create_connection()
    try:
        cursor.execute(
            "INSERT INTO agents (name, brokerage_rate) VALUES (?, ?)",
            (name, brokerage_rate)
        )
        con.commit()
        return cursor.lastrowid
    finally:
        con.close()

def get_agent_by_id(agent_id: int) -> Agent | None:
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()
        return _row_to_agent(row) if row else None
    finally:
        con.close()

def get_all_agents() -> list[Agent]:
    con, cursor = create_connection()
    try:
        cursor.execute("SELECT * FROM agents ORDER BY name")
        return [_row_to_agent(r) for r in cursor.fetchall()]
    finally:
        con.close()

def update_brokerage_rate(agent_id: int, new_rate: float) -> None:
    """Rates change over time — this updates going forward only. Past trades
    keep whatever entry_brokerage/exit_brokerage was already computed and
    stored at the time, since that's a snapshot, not a live lookup."""
    con, cursor = create_connection()
    try:
        cursor.execute(
            "UPDATE agents SET brokerage_rate = ? WHERE agent_id = ?",
            (new_rate, agent_id)
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Agent {agent_id} not found")
        con.commit()
    finally:
        con.close()

def search_agents_by_name(query: str) -> list[Agent]:
    con, cursor = create_connection()
    try:
        cursor.execute(
            "SELECT * FROM agents WHERE name LIKE ? ORDER BY name",
            (f"%{query}%",)
        )
        return [_row_to_agent(r) for r in cursor.fetchall()]
    finally:
        con.close()