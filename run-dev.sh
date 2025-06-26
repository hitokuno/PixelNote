#!/bin/bash
set -e

CONTAINER_NAME="pixelnote-dev"
docker ps -a

# 既存のコンテナが起動中なら停止
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
  echo "Stopping running container: $CONTAINER_NAME"
  docker stop "$CONTAINER_NAME"
fi

# 停止状態・終了済みのコンテナが存在すれば削除
if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
  echo "Removing existing container: $CONTAINER_NAME"
  docker rm "$CONTAINER_NAME"
fi

# 新規コンテナをバックグラウンド起動（最初は何もしないスリープ）
docker run -d \
  --name "$CONTAINER_NAME" \
  -p 8000:8000 \
  --env-file .env \
  pixelnote:latest sleep infinity

# 必要なファイル/フォルダをコピー
docker cp ./app "$CONTAINER_NAME":/app
docker cp ./tests "$CONTAINER_NAME":/app/tests
docker cp ./startup.sh "$CONTAINER_NAME":/app/startup.sh
docker cp ./.env "$CONTAINER_NAME":/app/.env

# （必要に応じてinit_sqlite.pyやinit_oracle.pyもcopy）
docker cp ./data/sqlite "$CONTAINER_NAME":/app/data/sqlite
docker cp ./scripts "$CONTAINER_NAME":/app/scripts

# コンテナ内でFastAPIを起動（リロード付き）
docker exec -d "$CONTAINER_NAME" bash -c "cd /app && chmod +x startup.sh && ./startup.sh"

echo "PixelNoteコンテナ($CONTAINER_NAME)がバックグラウンドで起動しました。"
echo "ログを見るには: docker logs -f $CONTAINER_NAME"
echo "停�