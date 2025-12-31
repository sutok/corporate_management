FROM python:3.11-slim

# 作業ディレクトリ設定
WORKDIR /app

# 環境変数設定
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# システムパッケージ更新とPostgreSQL依存関係インストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 依存関係ファイルコピー
COPY requirements.txt .

# Python依存関係インストール
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# アプリケーションコードコピー
COPY . .

# ポート公開
EXPOSE 8000

# アプリケーション起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
