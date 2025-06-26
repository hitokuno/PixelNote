#!/bin/bash
set -e

# .envの読込
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "==== Database mode: $DB_MODE ===="

# SQLiteの初期化
if [ "$DB_MODE" = "sqlite" ]; then
  if [ ! -f "$SQLITE_DB_PATH" ]; then
    echo "Initializing SQLite DB..."
    python app/db/init_sqlite.py
  fi
fi

# Oracleの初期化（必要ならDDL流すなど）
if [ "$DB_MODE" = "oracle" ]; then
  echo "Oracleは外部インスタンスに接続します"
  # 必要ならpython app/db/init_oracle.pyなど
fi

# サーバ起動
echo "==== Starting FastAPI server ===="
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app/app

echo "About to start uvicorn"
