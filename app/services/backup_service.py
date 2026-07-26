"""Manual backup: copies ledger.db to a timestamped file alongside it."""
import os
import shutil
from datetime import datetime

from app.database.connection import create_connection


def _db_path() -> str:
    con, cursor = create_connection()
    try:
        cursor.execute("PRAGMA database_list")
        row = cursor.fetchone()
        return row[2]
    finally:
        con.close()


def backup_now() -> str:
    db_path = _db_path()
    db_dir = os.path.dirname(db_path)
    backups_dir = os.path.join(db_dir, "backups")
    os.makedirs(backups_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backups_dir, f"ledger_backup_{timestamp}.db")

    shutil.copy2(db_path, backup_path)
    return backup_path


def last_backup_time() -> str | None:
    db_path = _db_path()
    backups_dir = os.path.join(os.path.dirname(db_path), "backups")
    if not os.path.isdir(backups_dir):
        return None

    backups = sorted(os.listdir(backups_dir), reverse=True)
    if not backups:
        return None
    mtime = os.path.getmtime(os.path.join(backups_dir, backups[0]))
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")