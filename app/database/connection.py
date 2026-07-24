import sqlite3 as sql
import os


def __get_secure_db_path():
    """Returns a secure path for the database file."""
    base_dir = os.environ.get('APPDATA') or os.path.expanduser('~')
    
    #Target folder: Appdata/Roaming/BrokeP
    target_folder = os.path.join(base_dir, 'BrokeP')

    #create the folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    return os.path.join(target_folder, 'ledger.db')


def create_connection():
    """Creates a connection to the database and returns con and cursor."""
    db_path = __get_secure_db_path()

    con = sql.connect(db_path)
    cursor = con.cursor()

    return con, cursor