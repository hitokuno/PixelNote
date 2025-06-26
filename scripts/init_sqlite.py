import sqlite3
import os

db_path = os.getenv("SQLITE_DB_PATH", "pixelnote.sqlite3")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# image_names テーブル
cur.execute("""
CREATE TABLE IF NOT EXISTS image_names (
    image_id TEXT PRIMARY KEY,
    image_name TEXT,
    last_modified_by TEXT,
    last_modified_at TEXT
);
""")

# drawings テーブル
cur.execute("""
CREATE TABLE IF NOT EXISTS drawings (
    drawing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id TEXT,
    version INTEGER,
    created_at TEXT,
    created_by TEXT
);
""")

# pixels テーブル
cur.execute("""
CREATE TABLE IF NOT EXISTS pixels (
    drawing_id INTEGER,
    x INTEGER,
    y INTEGER,
    rgb TEXT
);
""")

conn.commit()
conn.close()
print(f"Initialized SQLite DB at {db_path}")
