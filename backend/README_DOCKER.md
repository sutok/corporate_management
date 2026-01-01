# Docker セットアップガイド

## 概要

このプロジェクトはDocker Composeを使用して以下のサービスを管理します:
- **PostgreSQL**: データベース
- **Backend (FastAPI)**: RESTful API サーバー（**uv**使用で高速ビルド）
- **pgAdmin**: データベース管理ツール

### 技術的特徴

- ⚡ **高速パッケージ管理**: Rustベースの[uv](https://github.com/astral-sh/uv)を使用し、従来のpipより10-100倍高速
- 🔄 **ホットリロード**: コード変更時に自動的にサーバーが再起動
- 🔗 **サービス連携**: 専用ネットワークで各サービスが効率的に通信
- 📦 **データ永続化**: PostgreSQLデータとpgAdmin設定を永続化

## 前提条件

- Docker Desktop がインストールされていること
- Docker Compose がインストールされていること

## サービス構成

### 1. PostgreSQL (Database)
- **コンテナ名**: `attendance_db`
- **ポート**: `5432`
- **ユーザー**: `attendance_user`
- **パスワード**: `attendance_password`
- **データベース名**: `attendance_db`

### 2. Backend (FastAPI)
- **コンテナ名**: `attendance_backend`
- **ポート**: `8000`
- **パッケージマネージャー**: uv (Rust製、pip比10-100倍高速)
- **API URL**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**Dockerfileの最適化ポイント:**
```dockerfile
# uvを使用して高速インストール
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv pip install --system -r requirements.txt
```

詳細は [UV_GUIDE.md](./UV_GUIDE.md) を参照してください。

### 3. pgAdmin
- **コンテナ名**: `attendance_pgadmin`
- **ポート**: `5050`
- **URL**: http://localhost:5050
- **メール**: admin@attendance.local
- **パスワード**: admin

## 起動方法

### 初回起動

```bash
# プロジェクトルートディレクトリに移動
cd /Users/kazuh/Documents/GitHub/attendance

# Docker イメージをビルド
docker-compose build

# すべてのサービスを起動
docker-compose up -d

# ログを確認
docker-compose logs -f backend
```

### データベースマイグレーション

```bash
# backendコンテナに入る
docker-compose exec backend bash

# マイグレーション実行
alembic upgrade head

# コンテナから退出
exit
```

### サービス起動確認

```bash
# すべてのコンテナの状態確認
docker-compose ps

# バックエンドのログ確認
docker-compose logs -f backend

# データベース接続確認
docker-compose exec postgres psql -U attendance_user -d attendance_db -c "\dt"
```

## 便利なコマンド

### サービス管理

```bash
# すべてのサービスを起動
docker-compose up -d

# 特定のサービスのみ起動
docker-compose up -d postgres backend

# すべてのサービスを停止
docker-compose down

# サービスを停止してボリュームも削除
docker-compose down -v

# サービスを再起動
docker-compose restart backend

# サービスをリビルド
docker-compose build backend
docker-compose up -d backend
```

### ログ確認

```bash
# すべてのサービスのログ
docker-compose logs

# 特定サービスのログ (リアルタイム)
docker-compose logs -f backend

# 最新100行のログ
docker-compose logs --tail=100 backend
```

### コンテナ操作

```bash
# backendコンテナに入る
docker-compose exec backend bash

# PostgreSQLコンテナに入る
docker-compose exec postgres bash

# PostgreSQLに直接接続
docker-compose exec postgres psql -U attendance_user -d attendance_db

# backendコンテナでコマンド実行
docker-compose exec backend python -m pytest
```

### データベース操作

```bash
# データベースバックアップ
docker-compose exec postgres pg_dump -U attendance_user attendance_db > backup.sql

# データベースリストア
docker-compose exec -T postgres psql -U attendance_user -d attendance_db < backup.sql

# データベース再作成
docker-compose down -v
docker-compose up -d postgres
# データベースが起動するまで待機
sleep 10
docker-compose exec backend alembic upgrade head
```

## 開発ワークフロー

### 1. 初回セットアップ

```bash
# Dockerサービス起動
docker-compose up -d

# データベースマイグレーション
docker-compose exec backend alembic upgrade head

# テストデータ投入 (オプション)
docker-compose exec backend python scripts/seed_data.py
```

### 2. 開発中

```bash
# コードを編集 (ホストマシン)
# → バックエンドは自動リロードされる (--reload オプション有効)

# テスト実行
docker-compose exec backend pytest

# ログ確認
docker-compose logs -f backend
```

### 3. マイグレーション作成

```bash
# backendコンテナに入る
docker-compose exec backend bash

# マイグレーションファイル作成
alembic revision --autogenerate -m "Add new table"

# マイグレーション適用
alembic upgrade head

# exit
```

## トラブルシューティング

### ポートが既に使用されている

```bash
# 使用中のポート確認
lsof -i :8000
lsof -i :5432

# プロセスを終了
kill -9 <PID>
```

### データベース接続エラー

```bash
# PostgreSQLの起動確認
docker-compose ps postgres

# ヘルスチェック確認
docker-compose exec postgres pg_isready -U attendance_user -d attendance_db

# PostgreSQL再起動
docker-compose restart postgres
```

### コンテナが起動しない

```bash
# 詳細なログ確認
docker-compose logs backend

# コンテナをリビルド
docker-compose build --no-cache backend
docker-compose up -d backend
```

### データベースをリセット

```bash
# すべて削除して再作成
docker-compose down -v
docker-compose up -d
sleep 10
docker-compose exec backend alembic upgrade head
```

## 環境変数

バックエンドサービスの環境変数は `docker-compose.yml` で設定されています:

```yaml
environment:
  - APP_NAME=営業日報システムAPI
  - DATABASE_URL=postgresql://attendance_user:attendance_password@postgres:5432/attendance_db
  - DATABASE_URL_ASYNC=postgresql+asyncpg://attendance_user:attendance_password@postgres:5432/attendance_db
  - SECRET_KEY=your-secret-key-change-this-in-production
  - CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**注意**: 本番環境では `SECRET_KEY` を変更してください。

## 本番環境デプロイ

本番環境では以下の変更が推奨されます:

1. **環境変数を .env ファイルで管理**
   ```bash
   cp .env.example .env
   # .env ファイルを編集
   ```

2. **SECRET_KEY を強固なものに変更**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **DEBUG モードを無効化**
   ```yaml
   - DEBUG=false
   ```

4. **CORS_ORIGINS を制限**
   ```yaml
   - CORS_ORIGINS=https://yourdomain.com
   ```

5. **データベースパスワードを変更**

6. **ボリュームのバックアップ設定**

## API アクセス

### ヘルスチェック
```bash
curl http://localhost:8000/health
```

### API ドキュメント
ブラウザで http://localhost:8000/docs にアクセス

### 認証テスト
```bash
# ログイン
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# レスポンスのaccess_tokenを使用
TOKEN="<your-token>"

# 認証が必要なエンドポイントにアクセス
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```
