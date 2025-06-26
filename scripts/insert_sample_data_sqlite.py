import sqlite3
import os
import datetime
import uuid

db_path = os.getenv("SQLITE_DB_PATH", "pixelnote.sqlite3")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

now = datetime.datetime.utcnow().isoformat()
user = "sample_user"

# サンプル画像1
image_id1 = str(uuid.uuid4())
image_name1 = "サンプル画像1"
cur.execute(
    "INSERT INTO image_names (image_id, image_name, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?)",
    (image_id1, image_name1, user, now)
)
cur.execute(
    "INSERT INTO drawings (image_id, version, created_at, created_by) VALUES (?, ?, ?, ?)",
    (image_id1, 1, now, user)
)
drawing_id1 = cur.execute("SELECT last_insert_rowid()").fetchone()[0]
pixels1 = [(drawing_id1, x, y, "#ff0000") for x, y in [(0, 0), (10, 10), (20, 20)]]
cur.executemany("INSERT INTO pixels (drawing_id, x, y, rgb) VALUES (?, ?, ?, ?)", pixels1)

# サンプル画像2（バージョン2つ）
image_id2 = str(uuid.uuid4())
image_name2 = "サンプル画像2"
cur.execute(
    "INSERT INTO image_names (image_id, image_name, last_modified_by, last_modified_at) VALUES (?, ?, ?, ?)",
    (image_id2, image_name2, user, now)
)
# version 1
cur.execute(
    "INSERT INTO drawings (image_id, version, created_at, created_by) VALUES (?, ?, ?, ?)",
    (image_id2, 1, now, user)
)
drawing_id2_v1 = cur.execute("SELECT last_insert_rowid()").fetchone()[0]
pixels2_v1 = [(drawing_id2_v1, 5, 5, "#00ff00")]
cur.executemany("INSERT INTO pixels (drawing_id, x, y, rgb) VALUES (?, ?, ?, ?)", pixels2_v1)
# version 2
cur.execute(
    "INSERT INTO drawings (image_id, version, created_at, created_by) VALUES (?, ?, ?, ?)",
    (image_id2, 2, now, user)
)
drawing_id2_v2 = cur.execute("SELECT last_insert_rowid()").fetchone()[0]
pixels2_v2 = [(drawing_id2_v2, 6, 6, "#0000ff"), (drawing_id2_v2, 7, 7, "#ffff00")]
cur.executemany("INSERT INTO pixels (drawing_id, x, y, rgb) VALUES (?, ?, ?, ?)", pixels2_v2)

conn.commit()
conn.close()

print("サンプルデータを登録しました。")
