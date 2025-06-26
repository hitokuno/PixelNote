import oracledb
import os

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
dsn = os.getenv("DB_DSN")

conn = oracledb.connect(user=user, password=password, dsn=dsn)
cur = conn.cursor()

# image_names テーブル
cur.execute("""
BEGIN
    EXECUTE IMMEDIATE '
        CREATE TABLE image_names (
            image_id VARCHAR2(36) PRIMARY KEY,
            image_name VARCHAR2(255),
            last_modified_by VARCHAR2(255),
            last_modified_at TIMESTAMP
        )
    ';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -955 THEN -- -955: ORA-00955 name is already used by an existing object
            RAISE;
        END IF;
END;
""")

# drawings テーブル
cur.execute("""
BEGIN
    EXECUTE IMMEDIATE '
        CREATE TABLE drawings (
            drawing_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            image_id VARCHAR2(36),
            version NUMBER,
            created_at TIMESTAMP,
            created_by VARCHAR2(255)
        )
    ';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -955 THEN
            RAISE;
        END IF;
END;
""")

# pixels テーブル
cur.execute("""
BEGIN
    EXECUTE IMMEDIATE '
        CREATE TABLE pixels (
            drawing_id NUMBER,
            x INTEGER,
            y INTEGER,
            rgb VARCHAR2(7)
        )
    ';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -955 THEN
            RAISE;
        END IF;
END;
""")

conn.commit()
cur.close()
conn.close()
print("Initialized Oracle DB (if not already present)")
