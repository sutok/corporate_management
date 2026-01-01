FROM python:3.11-slim

# 作業ディレクトリ設定
WORKDIR /app

# 環境変数設定
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# システムパッケージ更新とPostgreSQL依存関係インストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    curl && \
    rm -rf /var/lib/apt/lists/*

# uvインストール
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx

# 依存関係ファイルコピー
COPY requirements.txt .

# Python依存関係インストール
RUN uv pip install --system -r requirements.txt

# アプリケーションコードコピー
COPY . .

# ポート公開
EXPOSE 8000

# アプリケーション起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
