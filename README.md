# 営業日報システム

営業担当者が日々の営業活動を報告し、上長が確認・コメントできる日報管理システム

## 技術スタック

### バックエンド
- **フレームワーク**: FastAPI (Python 3.11+)
- **データベース**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (非同期対応)
- **マイグレーション**: Alembic
- **認証**: JWT (python-jose)

### フロントエンド
- **フレームワーク**: React 18
- **ビルドツール**: Vite
- **言語**: TypeScript

### インフラ
- **開発環境**: Docker Compose
- **本番環境**: (予定) Terraform + AWS/GCP/Azure

## プロジェクト構造

```
attendance/
├── backend/                 # FastAPI バックエンド
│   ├── app/
│   │   ├── main.py         # FastAPIアプリケーション
│   │   ├── config.py       # 設定管理
│   │   ├── database.py     # DB接続
│   │   ├── models/         # SQLAlchemy モデル
│   │   ├── schemas/        # Pydantic スキーマ
│   │   ├── routers/        # APIエンドポイント
│   │   ├── services/       # ビジネスロジック
│   │   └── auth/           # JWT認証
│   ├── alembic/            # DBマイグレーション
│   ├── tests/
│   └── requirements.txt
├── frontend/               # React フロントエンド
│   └── (Vite + TypeScript)
├── docker-compose.yml      # PostgreSQL + 開発環境
└── claudedocs/             # 仕様書
    ├── CLAUDE.md           # 要件定義・ER図
    ├── 画面定義書.md       # 画面仕様
    ├── API設計書.md        # API仕様
    └── テスト仕様書.md     # テスト仕様
```

## セットアップ手順

### 1. 前提条件

- Python 3.11以上
- Node.js 18以上
- Docker & Docker Compose
- Git

### 2. リポジトリクローン

```bash
git clone <repository-url>
cd attendance
```

### 3. バックエンドセットアップ

```bash
cd backend

# Python仮想環境作成・有効化
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envファイルを編集して適切な値を設定
```

### 4. データベースセットアップ

```bash
# プロジェクトルートで実行
docker-compose up -d

# データベースが起動するまで待機（約10秒）
docker-compose ps

# マイグレーション実行（後で設定）
# cd backend
# alembic upgrade head
```

**PostgreSQL接続情報:**
- Host: localhost
- Port: 5432
- Database: attendance_db
- User: attendance_user
- Password: attendance_password

**pgAdmin接続情報:**
- URL: http://localhost:5050
- Email: admin@attendance.local
- Password: admin

### 5. バックエンド起動

```bash
cd backend

# 開発サーバー起動
python -m app.main

# または uvicorn直接実行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

APIドキュメント:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. フロントエンドセットアップ（後で実装）

```bash
cd frontend

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

## 開発ワークフロー

### データベースマイグレーション

```bash
cd backend

# マイグレーションファイル作成
alembic revision --autogenerate -m "migration message"

# マイグレーション実行
alembic upgrade head

# ロールバック
alembic downgrade -1
```

### テスト実行

```bash
cd backend

# テスト実行
pytest

# カバレッジ付き
pytest --cov=app --cov-report=html
```

## 仕様書

詳細な仕様は以下のドキュメントを参照してください：

- [要件定義・ER図](./claudedocs/CLAUDE.md)
- [画面定義書](./claudedocs/画面定義書.md)
- [API設計書](./claudedocs/API設計書.md)
- [テスト仕様書](./claudedocs/テスト仕様書.md)

## ライセンス

(ライセンスを記載)
