import pytest
from app.database import connection
from app.database.schema import TABLE_DEFINITIONS


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Redirects every create_connection() call to a fresh temp sqlite file
    for the duration of one test. Real ledger.db in AppData is never touched."""
    db_path = tmp_path / "test_ledger.db"

    monkeypatch.setattr(connection, "__get_secure_db_path", lambda: str(db_path))

    # build all tables on the fresh temp db
    con, cursor = connection.create_connection()
    for table_name, columns_sql in TABLE_DEFINITIONS.items():
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")
    con.commit()
    con.close()

    yield db_path
    # tmp_path is cleaned up automatically by pytest, no teardown needed