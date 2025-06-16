import oracledb
import os
from datetime import datetime
import uuid

class OracleDB:
    def __init__(self):
        self.pool = oracledb.create_pool(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN"),
            min=1,
            max=5,
            increment=1
        )

    # --- CRUD分離 ---
    def select_image_list(self, cur):
        cur.execute("SELECT image_id, image_name, last_modified_by, last_modified_at FROM image_names ORDER BY last_modified_at DESC")
        return [dict(row) for row in cur.fetchall()]

    def select_image_versions(self, cur, image_id):
        cur.execute(
            "SELECT version, created_at FROM drawings WHERE image_id=? ORDER BY created_at DESC",
            (image_id,)
        )
        return [str(row[0]) for row in cur.fetchall()]

    def select_drawing_data(self, cur, image_id, version):
        cur.execute("""
            SELECT x, y, rgb FROM pixels
            WHERE drawing_id = (
                SELECT drawing_id FROM drawings WHERE image_id = ? AND version = ?
            )
        """, (image_id, version))
        return [(r["x"], r["y"], r["rgb"]) for r in cur.fetchall()]
    
    def insert_image_name(self, cur, image_id, image_name, user_id, now):
        cur.execute(
            "INSERT INTO image_names (image_id, image_name, last_modified_by, last_modified_at) VALUES (:1, :2, :3, :4)",
            (image_id, image_name, user_id, now)
        )

    def insert_drawing(self, cur, image_id, version, user_id, now):
        did = cur.var(oracledb.NUMBER)
        cur.execute(
            "INSERT INTO drawings (image_id, version, created_at, created_by) VALUES (:1, :2, :3, :4) RETURNING drawing_id INTO :5",
            (image_id, version, now, user_id, did)
        )
        return int(did.getvalue())

    def insert_pixels(self, cur, drawing_id, pixels):
        cur.executemany(
            "INSERT INTO pixels (drawing_id, x, y, rgb) VALUES (:1, :2, :3, :4)",
            [(drawing_id, x, y, rgb) for x, y, rgb in pixels]
        )

    def update_image_name(self, cur, image_id, image_name, user_id, now):
        cur.execute(
            "UPDATE image_names SET image_name = :1, last_modified_by = :2, last_modified_at = :3 WHERE image_id = :4",
            (image_name, user_id, now, image_id)
        )

    def get_latest_version(self, cur, image_id):
        cur.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM drawings WHERE image_id = :1", (image_id,))
        return int(cur.fetchone()[0])

    def get_current_image_name(self, cur, image_id):
        cur.execute("SELECT image_name FROM image_names WHERE image_id = :1", (image_id,))
        row = cur.fetchone()
        return row[0] if row else None

    # --- API本体 ---
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
        now = datetime.utcnow()
        conn = self.pool.acquire()
        try:
            with conn.cursor() as cur:
                self.insert_image_name(cur, image_id, image_name, user_id, now)
                drawing_id = self.insert_drawing(cur, image_id, 1, user_id, now)
                self.insert_pixels(cur, drawing_id, pixels)
                conn.commit()
            return image_id
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"DB error (create_image): {e}")
        finally:
            conn.close()

    async def save_drawing(self, image_id, pixels, user_id):
        now = datetime.utcnow()
        conn = self.pool.acquire()
        try:
            with conn.cursor() as cur:
                version = self.get_latest_version(cur, image_id)
                drawing_id = self.insert_drawing(cur, image_id, version, user_id, now)
                self.insert_pixels(cur, drawing_id, pixels)
                current_name = self.get_current_image_name(cur, image_id)
                self.update_image_name(cur, image_id, current_name, user_id, now)
                conn.commit()
            return str(version)
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"DB error (save_drawing): {e}")
        finally:
            conn.close()

    async def rename_image(self, image_id, new_name, user_id):
        now = datetime.utcnow()
        conn = self.pool.acquire()
        try:
            with conn.cursor() as cur:
                self.update_image_name(cur, image_id, new_name, user_id, now)
                if cur.rowcount == 0:
                    raise ValueError("image_id not found")
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"DB error (rename_image): {e}")
        finally:
            conn.close()