import oracledb
import os
from typing import List, Tuple, Optional
from app.db.interface import DBInterface
from datetime import datetime
import uuid

class OracleDB(DBInterface):
    def __init__(self):
        self.pool = oracledb.create_pool(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN"),
            min=1,
            max=5,
            increment=1
        )

    def insert_image_name(self, cur, image_id, image_name, user_id, now):
        cur.execute("""
            INSERT INTO image_names (image_id, image_name, last_modified_by, last_modified_at)
            VALUES (:id, :name, :user, :at)
        """, {"id": image_id, "name": image_name, "user": user_id, "at": now})

    def insert_drawing(self, cur, image_id, version, user_id, now):
        did = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO drawings (image_id, version, created_at, created_by)
            VALUES (:id, :ver, :at, :by)
            RETURNING drawing_id INTO :did
        """, {"id": image_id, "ver": version, "at": now, "by": user_id, "did": did})
        return int(did.getvalue())

    def insert_pixels(self, cur, drawing_id, pixels):
        cur.executemany("""
            INSERT INTO pixels (drawing_id, x, y, rgb)
            VALUES (:did, :x, :y, :rgb)
        """, [{"did": drawing_id, "x": x, "y": y, "rgb": rgb} for x, y, rgb in pixels])

    def update_image_name(self, cur, image_id, image_name, user_id, now):
        cur.execute("""
            UPDATE image_names
            SET image_name = :name, last_modified_by = :user, last_modified_at = :at
            WHERE image_id = :id
        """, {"name": image_name, "user": user_id, "at": now, "id": image_id})

    async def create_image(self, image_name, pixels, user_id):
        image_id = str(uuid.uuid4())
        now = datetime.utcnow()
        with self.pool.acquire() as conn:
            with conn.cursor() as cur:
                self.insert_image_name(cur, image_id, image_name, user_id, now)
                drawing_id = self.insert_drawing(cur, image_id, 1, user_id, now)
                self.insert_pixels(cur, drawing_id, pixels)
        return image_id

    async def save_drawing(self, image_id, pixels, user_id):
        now = datetime.utcnow()
        with self.pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM drawings WHERE image_id = :id", {"id": image_id})
                version = int(cur.fetchone()[0])
                drawing_id = self.insert_drawing(cur, image_id, version, user_id, now)
                self.insert_pixels(cur, drawing_id, pixels)
                cur.execute("SELECT image_name FROM image_names WHERE image_id = :id", {"id": image_id})
                current_name = cur.fetchone()[0]
                self.update_image_name(cur, image_id, current_name, user_id, now)
        return str(version)

    async def rename_image(self, image_id, new_name, user_id):
        now = datetime.utcnow()
        with self.pool.acquire() as conn:
            with conn.cursor() as cur:
                self.update_image_name(cur, image_id, new_name, user_id, now)

    async def get_image_list(self):
        with self.pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT image_id, image_name, last_modified_by, last_modified_at FROM image_names")
                rows = cur.fetchall()
                return [
                    {
                        "image_id": r[0],
                        "image_name": r[1],
                        "last_modified_by": r[2],
                        "last_modified_at": r[3].isoformat()
                    } for r in rows
                ]

    async def get_image_versions(self, image_id):
        with self.pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version FROM drawings WHERE image_id = :id ORDER BY version DESC", {"id": image_id})
                return [str(r[0]) for r in cur.fetchall()]

    async def get_drawing_data(self, image_id, version):
        with self.pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT x, y, rgb FROM pixels
                    WHERE drawing_id = (
                        SELECT drawing_id FROM drawings WHERE image_id = :id AND version = :ver
                    )
                """, {"id": image_id, "ver": version})
                rows = cur.fetchall()
                return [(r[0], r[1], r[2]) for r in rows] if rows else None
