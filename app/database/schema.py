from app.database.connection import create_connection

TABLE_DEFINITIONS = {
    "clients": """
        client_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        created_at  TEXT NOT NULL
    """,
    "agents": """
        agent_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT NOT NULL,
        brokerage_rate  REAL NOT NULL
    """,
    "trades": """
        trade_id            INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id           INTEGER NOT NULL REFERENCES clients(client_id),
        agent_id            INTEGER NOT NULL REFERENCES agents(agent_id),
        segment             TEXT NOT NULL,
        symbol              TEXT NOT NULL,
        quantity            INTEGER NOT NULL,
        entry_date          TEXT NOT NULL,
        entry_price         REAL NOT NULL,
        entry_brokerage     REAL NOT NULL,
        entry_service_fee   REAL DEFAULT 0,
        status              TEXT NOT NULL,
        exit_date           TEXT,
        exit_price          REAL,
        exit_brokerage      REAL,
        exit_service_fee    REAL DEFAULT 0,
        gross_pl            REAL,
        net_pl              REAL,
        remarks             TEXT
    """,
    "cash_transactions": """
        txn_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id   INTEGER NOT NULL REFERENCES clients(client_id),
        txn_date    TEXT NOT NULL,
        txn_type    TEXT NOT NULL,
        amount      REAL NOT NULL,
        remarks     TEXT
    """,
    "daily_marks": """
    mark_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id             INTEGER NOT NULL REFERENCES trades(trade_id),
    mark_date            TEXT NOT NULL,
    closing_price        REAL NOT NULL,
    unrealized_gross_pl  REAL NOT NULL,
    unrealized_net_pl    REAL NOT NULL,
    UNIQUE(trade_id, mark_date)
    """
}


def create_table(cursor, table_name: str, columns_sql: str):
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")


def create_all_tables():
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