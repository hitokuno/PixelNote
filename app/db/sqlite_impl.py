import sqlite3
from datetime import datetime
from typing import List, Tuple
import uuid
from fastapi.exceptions import RequestValidationError

class SQLiteDB:
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

    # ---- CRUD細分化 ----
    def select_image_list(self, cur):
        cur.execute(
            "SELECT image_id, image_name, last_modified_by, last_modified_at FROM image_names ORDER BY last_modified_at DESC"
        )
        return [dict(row) for row in cur.fetchall()]

    def select_image_versions(self, cur, image_id):
        cur.execute(
            "SELECT version, created_at, created_by FROM drawings WHERE image_id=? ORDER BY created_at DESC",
            (image_id,)
        )
        return [str(row[0]) for row in cur.fetchall()]

    def select_drawing_data(self, cur, image_id, version):
        cur.execute("""
            SELECT x, y, rgb FROM pixels
            WHERE drawing_id = (
                SELECT drawing_id FROM drawings WHERE image_id = ? AND version = ?
            )
            ORDER BY x, y                    
        """, (image_id, version))
        return [(r["x"], r["y"], r["rgb"]) for r in cur.fetchall()]
    
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

    def get_latest_version(self, cur, image_id):
        cur.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM drawings WHERE image_id=?", (image_id,))
        return cur.fetchone()[0]

    def get_current_image_name(self, cur, image_id):
        cur.execute("SELECT image_name FROM image_names WHERE image_id=?", (image_id,))
        row = cur.fetchone()
        return row[0] if row else None

        # ---- API本体 ----
    async def get_image_list(self):
        cur = self.conn.cursor()
        return self.select_image_list(cur)
    
    async def get_image_versions(self, image_id):
        cur = self.conn.cursor()
        return self.select_image_versions(cur, image_id)
    
    async def get_drawing_data(self, image_id, version):
        cur = self.conn.cursor()
        return self.select_drawing_data(cur, image_id, version)

    async def create_image(self, image_name, pixels, user_id):
        image_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        try:
            cur = self.conn.cursor()
            self.insert_image_name(cur, image_id, image_name, user_id, now)
            drawing_id = self.insert_drawing(cur, image_id, 1, user_id, now)
            self.insert_pixels(cur, drawing_id, pixels)
            self.conn.commit()
            return image_id
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"DB error (create_image): {e}")

    async def save_drawing(self, image_id, pixels, user_id):
        now = datetime.utcnow().isoformat()
        try:
            cur = self.conn.cursor()
            version = self.get_latest_version(cur, image_id)
            drawing_id = self.insert_drawing(cur, image_id, version, user_id, now)
            self.insert_pixels(cur, drawing_id, pixels)
            current_name = self.get_current_image_name(cur, image_id)
            self.update_image_name(cur, image_id, current_name, user_id, now)
            self.conn.commit()
            return str(version)
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"DB error (save_drawing): {e}")

    async def rename_image(self, image_id, new_name, user_id):
        now = datetime.utcnow().isoformat()
        try:
            cur = self.conn.cursor()
            self.update_image_name(cur, image_id, new_name, user_id, now)
            if cur.rowcount == 0:
                raise RequestValidationError([{
                    "loc": ("body", "image_id"),
                    "msg": "指定したimage_idが存在しません",
                    "type": "value_error.notfound",
                    "input": image_id
                }])
            self.conn.commit()
        except RequestValidationError:
            self.conn.rollback()
            raise
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"DB error (rename_image): {e}")
