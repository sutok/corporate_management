# トラブルシューティングガイド

## 目次
1. [make db-reset エラー](#make-db-reset-エラー)
2. [psql: command not found](#psql-command-not-found)
3. [データベース接続エラー](#データベース接続エラー)
4. [マイグレーションエラー](#マイグレーションエラー)
5. [テスト失敗](#テスト失敗)

---

## make db-reset エラー

### 問題: `make: *** No rule to make target 'db-reset'. Stop.`

**原因:** Makefileが存在しないか、`db-reset` ターゲットが定義されていない

**解決方法:**

1. Makefileが存在するか確認:
```bash
ls -la Makefile
```

2. Makefileが存在しない場合は作成されているはずです。利用可能なコマンドを確認:
```bash
make help
```

3. `db-reset`が表示されれば成功です

---

## psql: command not found

### 問題: `psql` コマンドが見つからない

**原因:** PostgreSQLクライアントツールがPATHに含まれていない

**解決方法:**

### macOS の場合:

1. PostgreSQL がインストールされているか確認:
```bash
which psql
```

2. インストールされているが見つからない場合、PATHに追加:
```bash
# Homebrewでインストールした場合
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# または
export PATH="/usr/local/opt/postgresql@15/bin:$PATH"
```

3. `.zshrc` または `.bashrc` に追加して永続化:
```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 代替方法: Pythonスクリプトで直接実行

`psql` が使えない場合は、Pythonスクリプトで直接データベース操作を実行できます:

```bash
# データベースリセット（Python経由）
python scripts/reset_database.py --yes

# または個別に実行
DATABASE_URL_ASYNC="postgresql+asyncpg://postgres:postgres@localhost:5432/corporate_management_db" \
  python scripts/seed_test_data.py
```

---

## データベース接続エラー

### 問題: `Connection refused` または `could not connect to server`

**原因:** PostgreSQLサーバーが起動していない、または接続情報が間違っている

**診断手順:**

1. PostgreSQLサーバーが起動しているか確認:
```bash
# macOS (Homebrew)
brew services list | grep postgresql

# または
ps aux | grep postgres
```

2. サーバーを起動:
```bash
# macOS (Homebrew)
brew services start postgresql@15

# Linux (systemd)
sudo systemctl start postgresql
```

3. 接続情報を確認:
```bash
# デフォルト設定
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=corporate_management_db
```

4. 手動で接続テスト:
```bash
psql -h localhost -U postgres -d corporate_management_db
```

### 問題: `FATAL: password authentication failed`

**原因:** パスワードが間違っている

**解決方法:**

1. PostgreSQLのパスワードを設定:
```sql
-- psqlで実行
ALTER USER postgres WITH PASSWORD 'postgres';
```

2. Makefileの環境変数を更新:
```bash
# backend/Makefile
DB_PASS ?= your_actual_password
```

---

## マイグレーションエラー

### 問題: `Target database is not up to date`

**原因:** マイグレーションが最新ではない

**解決方法:**

1. 現在のバージョンを確認:
```bash
make db-migrate-current
```

2. マイグレーションを実行:
```bash
make db-migrate
```

3. マイグレーション履歴を確認:
```bash
make db-migrate-history
```

### 問題: `Can't locate revision identified by 'xxxxx'`

**原因:** マイグレーションファイルが見つからない、またはバージョン不整合

**解決方法:**

1. マイグレーション履歴を確認:
```bash
ls -la alembic/versions/
```

2. データベースを完全にリセット:
```bash
make db-reset-auto
```

---

## テスト失敗

### 問題: テストが失敗する

**診断手順:**

1. 詳細なエラーメッセージを確認:
```bash
make test
```

2. 特定のテストを実行:
```bash
.venv/bin/pytest tests/test_auth.py -v
```

3. テストデータベースを確認:
```bash
# テスト実行時は別のデータベースを使用することを推奨
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_db"
```

### 問題: `UserGroupAssignment` 関連のエラー

**原因:** `assigned_at` フィールドがNULLになっている

**解決方法:**

`scripts/seed_test_data.py` または `scripts/seed_users.py` を確認:
```python
UserGroupAssignment(
    user_id=user.id,
    group_role_id=group_role.id,
    assigned_at=datetime.now(),  # この行が必要
)
```

---

## よくある質問

### Q: `make db-reset` が確認プロンプトを出さずに実行したい

**A:** `make db-reset-auto` を使用してください（CI/CD用）:
```bash
make db-reset-auto
```

### Q: データベースをリセットせずにマイグレーションだけ実行したい

**A:**
```bash
make db-migrate
```

### Q: ユーザーデータだけをリセットしたい

**A:**
```bash
make db-seed-users-clear
```

### Q: カスタムのデータベース名を使いたい

**A:** 環境変数で上書きできます:
```bash
DB_NAME=my_custom_db make db-reset
```

---

## 環境変数の設定

開発をスムーズにするため、`.env` ファイルを作成することをお勧めします:

```bash
# backend/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/corporate_management_db
DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:postgres@localhost:5432/corporate_management_db
SECRET_KEY=your-secret-key-change-this-in-production
```

`.env` ファイルは自動的に読み込まれます（`python-dotenv` が必要）。

---

## デバッグモード

より詳細なログを確認したい場合:

```bash
# SQLログを有効化
export SQLALCHEMY_ECHO=1

# アプリケーションログレベルを変更
export LOG_LEVEL=DEBUG

# 開発サーバーを起動
make dev
```

---

## サポートが必要な場合

1. エラーメッセージの全文をコピー
2. 実行したコマンドを記録
3. 環境情報を確認:
   ```bash
   python --version
   psql --version
   uname -a
   ```
4. Issue を作成: https://github.com/your-repo/issues
