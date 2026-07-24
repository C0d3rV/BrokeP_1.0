from app.database.connection import create_connection



# Each table maps to its column definitions as raw SQL fragments.
# Order matters (matches your data model doc), constraints live right next to the column.
TABLE_DEFINITIONS = {
    "clients": """
        client_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        created_at  TEXT NOT NULL
    """,
    "trades": """
        trade_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id       INTEGER NOT NULL REFERENCES clients(client_id),
        agent_id        INTEGER REFERENCES agents(agent_id),
        segment         TEXT NOT NULL,
        symbol          TEXT NOT NULL,
        quantity        INTEGER NOT NULL,
        entry_date      TEXT NOT NULL,
        entry_price     REAL NOT NULL,
        entry_brokerage REAL NOT NULL,
        status          TEXT NOT NULL,
        exit_date       TEXT,
        exit_price      REAL,
        exit_brokerage  REAL,
        service_fee     REAL DEFAULT 0,
        gross_pl        REAL,
        net_pl          REAL,
        remarks         TEXT
    """,
    "cash_transactions": """
        txn_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id   INTEGER NOT NULL REFERENCES clients(client_id),
        txn_date    TEXT NOT NULL,
        txn_type    TEXT NOT NULL,
        amount      REAL NOT NULL,
        remarks     TEXT
    """,
    "agents": """
        agent_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        brokerage_rate REAL NOT NULL
    """
}


def create_table(cursor, table_name: str, columns_sql: str):
    """Generic single-table creator. Table name and column SQL are trusted
    (hardcoded above), never user input — so f-string here is safe."""
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")


def create_all_tables():
    """Call this once at app startup."""
    con, cursor = create_connection()
    try:
        for table_name, columns_sql in TABLE_DEFINITIONS.items():
            create_table(cursor, table_name, columns_sql)
        con.commit()
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise e
    finally:
        con.close()