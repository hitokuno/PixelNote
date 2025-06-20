import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional
from app.db.interface import DBInterface
import uuid

class SQLiteDB(DBInterface):
    def __init__(self):
        self.conn = sqlite3.connect("sqlite.db", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        cur = self.conn.cursor()
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
        self.conn.commit()

    def insert_image_name(self, cur, image_id, image_name, user_id, now):
        cur.execute(
            "INSERT INTO image_names VALUES (?, ?, ?, ?)",
            (image_id, image_name, user_id, now)
        )

    def insert_drawing(self, cur, image_id, version, user_id, now):
        cur.execute(
            "INSERT INTO drawings (image_id, version, created_at, created_by) VALUES (?, ?, ?, ?)",
            (image_id, version, now, user_id)
        )
        return cur.lastrowid

    def insert_pixels(self, cur, drawing_id, pixels):
        cur.executemany(
            "INSERT INTO pixels (drawing_id, x, y, rgb) VALUES (?, ?, ?, ?)",
            [(drawing_id, x, y, rgb) for x, y, rgb in pixels]
        )

    def update_image_name(self, cur, image_id, image_name, user_id, now):
        cur.execute(
            "UPDATE image_names SET image_name=?, last_modified_by=?, last_modified_at=? WHERE image_id=?",
            (image_name, user_id, now, image_id)
        )

    async def create_image(self, image_name, pixels, user_id):
        if len(image_name) > 255:
            raise ValueError("image_name too long")
        image_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        cur = self.conn.cursor()
        self.insert_image_name(cur, image_id, image_name, user_id, now)
        drawing_id = self.insert_drawing(cur, image_id, 1, user_id, now)
        self.insert_pixels(cur, drawing_id, pixels)
        self.conn.commit()
        return image_id

    async def save_drawing(self, image_id, pixels, user_id):
        now = datetime.utcnow().isoformat()
        cur = self.conn.cursor()
        cur.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM drawings WHERE image_id=?", (image_id,))
        version = cur.fetchone()[0]
        drawing_id = self.insert_drawing(cur, image_id, version, user_id, now)
        self.insert_pixels(cur, drawing_id, pixels)
        cur.execute("SELECT image_name FROM image_names WHERE image_id=?", (image_id,))
        current_name = cur.fetchone()[0]
        self.update_image_name(cur, image_id, current_name, user_id, now)
        self.conn.commit()
        return str(version)

    async def rename_image(self, image_id, new_name, user_id):
        now = datetime.utcnow().isoformat()
        cur = self.conn.cursor()
        self.update_image_name(cur, image_id, new_name, user_id, now)
        if cur.rowcount == 0:
            raise ValueError("image_id not found")
        self.conn.commit()

    async def get_image_list(self):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT image_id, image_name, last_modified_by, last_modified_at FROM image_names ORDER BY last_modified_at DESC"
        )
        return [dict(row) for row in cur.fetchall()]

    async def get_image_versions(self, image_id):
        cur = self.conn.cursor()
        cur.execute("SELECT version FROM drawings WHERE image_id=? ORDER BY version DESC", (image_id,))
        return [str(row[0]) for row in cur.fetchall()]

    async def get_drawing_data(self, image_id, version):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT drawing_id FROM drawings WHERE image_id=? AND version=?",
            (image_id, version),
        )
        row = cur.fetchone()
        if row is None:
            return None
        drawing_id = row["drawing_id"]
        cur.execute(
            "SELECT x, y, rgb FROM pixels WHERE drawing_id=?",
            (drawing_id,),
        )
        return [(r["x"], r["y"], r["rgb"]) for r in cur.fetchall()]
