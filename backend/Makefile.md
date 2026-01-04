# Makefile コマンドリファレンス

## 概要

このプロジェクトでは `make` コマンドを使用して、一般的な開発タスクを簡素化しています。

## クイックスタート

```bash
# 利用可能なコマンドを表示
make help

# 初回セットアップ（依存関係インストール + データベースリセット）
make init

# データベースリセット（全削除 → マイグレーション → 権限初期化 → テストデータ投入）
make db-reset-auto

# 開発サーバーを起動
make dev
```

## データベースコマンド

### `make db-reset`
データベースを完全にリセットします（確認プロンプトあり）。

**実行内容:**
1. データベース削除
2. データベース作成
3. マイグレーション実行
4. 権限システム初期化（GroupRole + Role + 割り当て）
5. テストデータ投入（企業、支店、部署、ユーザー、サービス、契約）

**注意:** `psql` コマンドが利用できない場合、自動的にPythonスクリプト (`scripts/reset_database.py`) にフォールバックします。

### `make db-reset-auto`
確認プロンプトなしでデータベースをリセットします（CI/CD用）。

### `make db-migrate`
マイグレーションを最新バージョンに実行します。

```bash
make db-migrate
```

### `make db-migrate-create`
新しいマイグレーションファイルを作成します。

```bash
make db-migrate-create
# プロンプトでマイグレーション名を入力
```

### `make db-migrate-downgrade`
マイグレーションを1つ戻します。

### `make db-seed`
完全なテストデータを投入します。

### `make db-seed-users`
ユーザーデータのみを投入します（追加モード）。

### `make db-seed-users-clear`
既存ユーザーをクリアして新しいユーザーを投入します。

### `make db-shell`
PostgreSQL シェルを起動します。

### `make db-status`
データベース接続とマイグレーション状態を確認します。

## 開発コマンド

### `make install`
依存関係をインストールします。

```bash
make install
```

### `make dev`
開発サーバーを起動します（ホットリロード有効）。

```bash
make dev
# http://localhost:8000 でアクセス可能
```

### `make test`
テストを実行します。

```bash
make test
```

### `make test-cov`
カバレッジ付きでテストを実行します。

```bash
make test-cov
# htmlcov/index.html でレポートを確認
```

### `make lint`
コードのlintチェックを実行します。

```bash
make lint
```

### `make format`
コードをフォーマットします（black + isort）。

```bash
make format
```

### `make clean`
一時ファイルを削除します（__pycache__, *.pyc, .pytest_cache など）。

```bash
make clean
```

### `make check`
全チェックを実行します（lint + test）。

```bash
make check
```

## ユーティリティコマンド

### `make shell`
Pythonシェルを起動します。

```bash
make shell
```

### `make routes`
APIルート一覧を表示します。

```bash
make routes
```

## Dockerコマンド

### `make docker-up`
Dockerコンテナを起動します。

```bash
make docker-up
```

### `make docker-down`
Dockerコンテナを停止します。

```bash
make docker-down
```

### `make docker-logs`
Dockerログを表示します。

```bash
make docker-logs
```

### `make docker-ps`
実行中のコンテナを表示します。

```bash
make docker-ps
```

## 環境変数のカスタマイズ

デフォルトの環境変数を上書きできます：

```bash
# カスタムデータベース名でリセット
DB_NAME=my_custom_db make db-reset

# カスタム認証情報
DB_USER=myuser DB_PASS=mypass make db-migrate
```

**デフォルト値:**
- `DB_NAME`: corporate_management_db
- `DB_USER`: postgres
- `DB_PASS`: postgres
- `DB_HOST`: localhost
- `DB_PORT`: 5432

## トラブルシューティング

### `psql: command not found`

`psql` コマンドが見つからない場合、Makefileは自動的にPythonスクリプトを使用します。

手動で実行する場合：
```bash
python scripts/reset_database.py --yes
```

### データベース接続エラー

PostgreSQLが起動しているか確認：
```bash
# macOS (Homebrew)
brew services list | grep postgresql

# 起動
brew services start postgresql@15
```

詳細は `TROUBLESHOOTING.md` を参照してください。

## ワークフロー例

### 初回セットアップ
```bash
make init
```

### 日常的な開発
```bash
# 開発サーバー起動
make dev

# 別のターミナルでテスト実行
make test

# コードフォーマット
make format
```

### マイグレーション作成
```bash
# モデルを変更
# ...

# マイグレーション作成
make db-migrate-create
# マイグレーション名入力: add_new_field

# マイグレーション適用
make db-migrate
```

### データベースリセット
```bash
# 完全リセット
make db-reset-auto

# または確認付き
make db-reset
```

## さらなる情報

- スクリプトの詳細: `scripts/README.md`
- トラブルシューティング: `TROUBLESHOOTING.md`
- API仕様: `claudedocs/API設計書.md`
