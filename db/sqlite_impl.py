import sqlite3
from typing import List, Tuple, Optional
from db.interface import DBInterface
from datetime import datetime
import uuid

class SQLiteDB(DBInterface):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def insert_image_name(self, cur, image_id, image_name, user_id, now):
        cur.execute("""
            INSERT INTO image_names (image_id, image_name, last_modified_by, last_modified_at)
            VALUES (?, ?, ?, ?)
        """, (image_id, image_name, user_id, now))

    def insert_drawing(self, cur, image_id, version, user_id, now):
        cur.execute("""
            INSERT INTO drawings (image_id, version, created_at, created_by)
            VALUES (?, ?, ?, ?)
        """, (image_id, version, now, user_id))
        return cur.lastrowid

    def insert_pixels(self, cur, drawing_id, pixels):
        cur.executemany("""
            INSERT INTO pixels (drawing_id, x, y, rgb)
            VALUES (?, ?, ?, ?)
        """, [(drawing_id, x, y, rgb) for x, y, rgb in pixels])

    def update_image_name(self, cur, image_id, image_name, user_id, now):
        cur.execute("""
            UPDATE image_names
            SET image_name = ?, last_modified_by = ?, last_modified_at = ?
            WHERE image_id = ?
        """, (image_name, user_id, now, image_id))

    async def create_image(self, image_name: str, pixels: List[Tuple[int, int, str]], user_id: str) -> str:
        image_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            cur = conn.cursor()
            self.insert_image_name(cur, image_id, image_name, user_id, now)
            drawing_id = self.insert_drawing(cur, image_id, 1, user_id, now)
            self.insert_pixels(cur, drawing_id, pixels)
            conn.commit()
        return image_id

    async def save_drawing(self, image_id: str, pixels: List[Tuple[int, int, str]], user_id: str) -> str:
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM drawings WHERE image_id = ?", (image_id,))
            version = int(cur.fetchone()[0])
            drawing_id = self.insert_drawing(cur, image_id, version, user_id, now)
            self.insert_pixels(cur, drawing_id, pixels)
            cur.execute("SELECT image_name FROM image_names WHERE image_id = ?", (image_id,))
            row = cur.fetchone()
            current_name = row[0] if row else ""
            self.update_image_name(cur, image_id, current_name, user_id, now)
            conn.commit()
        return str(version)

    async def rename_image(self, image_id: str, new_name: str, user_id: str) -> None:
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            cur = conn.cursor()
            self.update_image_name(cur, image_id, new_name, user_id, now)
            conn.commit()

    async def get_image_list(self) -> List[dict]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT image_id, image_name, last_modified_by, last_modified_at FROM image_names")
            return [
                {
                    "image_id": r[0],
                    "image_name": r[1],
                    "last_modified_by": r[2],
                    "last_modified_at": r[3]
                } for r in cur.fetchall()
            ]

    async def get_image_versions(self, image_id: str) -> List[str]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT version FROM drawings WHERE image_id = ? ORDER BY version DESC", (image_id,))
            return [str(r[0]) for r in cur.fetchall()]

    async def get_drawing_data(self, image_id: str, version: int) -> Optional[List[Tuple[int, int, str]]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT x, y, rgb FROM pixels
                WHERE drawing_id = (
                    SELECT drawing_id FROM drawings WHERE image_id = ? AND version = ?
                )
            """, (image_id, version))
            rows = cur.fetchall()
            return [(r[0], r[1], r[2]) for r in rows] if rows else None
