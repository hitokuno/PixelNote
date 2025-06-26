import oracledb
import os
import datetime
import uuid

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
dsn = os.getenv("DB_DSN")

conn = oracledb.connect(user=user, password=password, dsn=dsn)
cur = conn.cursor()

now = datetime.datetime.utcnow()
user_id = "sample_user"

# サンプル画像1
image_id1 = str(uuid.uuid4())
image_name1 = "サンプル画像1"
cur.execute(
    "INSERT INTO image_names (image_id, image_name, last_modified_by, last_modified_at) VALUES (:id, :name, :user, :at)",
    {"id": image_id1, "name": image_name1, "user": user_id, "at": now}
)
cur.execute(
    "INSERT INTO drawings (image_id, version, created_at, created_by) VALUES (:id, :ver, :at, :by) RETURNING drawing_id INTO :did",
    {"id": image_id1, "ver": 1, "at": now, "by": user_id, "did": cur.var(oracledb.NUMBER)}
)
drawing_id1 = int(cur.getvalue(0))
pixels1 = [(drawing_id1, x, y, "#ff0000") for x, y in [(0, 0), (10, 10), (20, 20)]]
cur.executemany("INSERT INTO pixels (drawing_id, x, y, rgb) VALUES (:d, :x, :y, :rgb)", [
    {"d": p[0], "x": p[1], "y": p[2], "rgb": p[3]} for p in pixels1
])

# サンプル画像2（バージョン2つ）
image_id2 = str(uuid.uuid4())
image_name2 = "サンプル画像2"
cur.execute(
    "INSERT INTO image_names (image_id, image_name, last_modified_by, last_modified_at) VALUES (:id, :name, :user, :at)",
    {"id": image_id2, "name": image_name2, "user": user_id, "at": now}
)
# version 1
cur.execute(
    "INSERT INTO drawings (image_id, version, created_at, created_by) VALUES (:id, :ver, :at, :by) RETURNING drawing_id INTO :did",
    {"id": image_id2, "ver": 1, "at": now, "by": user_id, "did": cur.var(oracledb.NUMBER)}
)
drawing_id2_v1 = int(cur.getvalue(0))
pixels2_v1 = [(drawing_id2_v1, 5, 5, "#00ff00")]
cur.executemany("INSERT INTO pixels (drawing_id, x, y, rgb) VALUES (:d, :x, :y, :rgb)", [
    {"d": p[0], "x": p[1], "y": p[2], "rgb": p[3]} for p in pixels2_v1
])
# version 2
cur.execute(
    "INSERT INTO drawings (image_id, version, created_at, created_by) VALUES (:id, :ver, :at, :by) RETURNING drawing_id INTO :did",
    {"id": image_id2, "ver": 2, "at": now, "by": user_id, "did": cur.var(oracledb.NUMBER)}
)
drawing_id2_v2 = int(cur.getvalue(0))
pixels2_v2 = [(drawing_id2_v2, 6, 6, "#0000ff"), (drawing_id2_v2, 7, 7, "#ffff00")]
cur.executemany("INSERT INTO pixels (drawing_id, x, y, rgb) VALUES (:d, :x, :y, :rgb)", [
    {"d": p[0], "x": p[1], "y": p[2], "rgb": p[3]} for p in pixels2_v2
])

conn.commit()
cur.close()
conn.close()

print("サンプルデータをOracleに登録しました。")
