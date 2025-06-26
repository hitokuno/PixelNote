FROM python:3.11-slim

WORKDIR /app

# 必要パッケージのインストール（procps, nano, curl, wgetを追加）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        procps \
        nano \
        curl \
        wget \
    && rm -rf /var/lib/apt/lists/*

# 依存インストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体と初期化スクリプトをコピー
COPY app/ ./app/
COPY data/sqlite/ ./data/sqlite/
COPY scripts/ ./scripts/
COPY .env ./
COPY startup.sh ./startup.sh

# スタートアップスクリプトに実行権限を付与
RUN chmod +x ./startup.sh

# Entrypointでstartup.shを実行
ENTRYPOINT ["sh", "./startup.sh"]
