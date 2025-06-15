import sqlite3
import os

def initialize_database(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS image_names (
        image_id TEXT PRIMARY KEY,
        image_name TEXT,
        last_modified_by TEXT,
        last_modified_at TEXT
    );

    CREATE TABLE IF NOT EXISTS drawings (
        drawing_id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_id TEXT,
        version INTEGER,
        created_at TEXT,
        created_by TEXT
    );

    CREATE TABLE IF NOT EXISTS pixels (
        drawing_id INTEGER,
        x INTEGER,
        y INTEGER,
        rgb TEXT
    );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    path = os.getenv("SQLITE_PATH", "dev.db")
    initialize_database(path)
