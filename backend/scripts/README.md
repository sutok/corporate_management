# テストデータ投入スクリプト

このディレクトリには、開発・テスト用のデータ投入スクリプトが含まれています。

## スクリプト一覧

### 1. `seed_test_data.py` - 完全なテストデータセット

企業、支店、部署、ユーザー、サービス、契約を含む完全なテストデータを投入します。

**使い方:**
```bash
DATABASE_URL="postgresql://..." DATABASE_URL_ASYNC="postgresql+asyncpg://..." \
  python scripts/seed_test_data.py
```

**作成されるデータ:**
- 企業: 2社（東京商事株式会社、大阪物産株式会社）
- 支店: 各企業2支店（計4支店）
- 部署: 各支店1部署（計4部署）
- ユーザー: 5名
  - 東京商事: システム管理者(admin)、一般スタッフ、マネージャー
  - 大阪物産: 一般スタッフ、マネージャー
- サービス: 2件（組織管理、日報管理）
- サービス契約: 4件（全企業が全サービスを契約）

**主なログイン情報:**
- 管理者: `admin@tokyo-shoji.co.jp` / `admin123` ★全権限
- スタッフ: `yamada@tokyo-shoji.co.jp` / `password123`
- マネージャー: `sato@tokyo-shoji.co.jp` / `password123`

---

### 2. `seed_users.py` - ユーザーデータ専用

既存の企業データを前提として、テストユーザーのみを投入します。

**使い方:**
```bash
# 追加モード（既存ユーザーはそのまま）
DATABASE_URL="postgresql://..." DATABASE_URL_ASYNC="postgresql+asyncpg://..." \
  python scripts/seed_users.py

# クリアモード（既存ユーザーを削除してから投入）
DATABASE_URL="postgresql://..." DATABASE_URL_ASYNC="postgresql+asyncpg://..." \
  python scripts/seed_users.py --clear --yes
```

**オプション:**
- `--clear`: 既存のユーザーデータをクリアしてから投入
- `--yes`: 確認プロンプトをスキップして実行

**作成されるデータ:**
企業ごとに以下のユーザーが作成されます：

**東京商事株式会社（company1）:**
- システム管理者: `admin@company1.example.com` / `admin123` ★全権限
- 営業部長: `sales-manager@company1.example.com` / `password123`
- 営業担当A: `sales-a@company1.example.com` / `password123`
- 営業担当B: `sales-b@company1.example.com` / `password123`
- 総務担当: `general-affairs@company1.example.com` / `password123`

**大阪物産株式会社（company2）:**
- 管理者: `admin@company2.example.com` / `password123`
- スタッフ1: `staff1-1@company2.example.com` / `password123`
- スタッフ2: `staff1-2@company2.example.com` / `password123`

**グループ別内訳:**
- 管理者グループ: 1名（全権限）
- マネージャーグループ: 2名
- 一般スタッフグループ: 5名

**注意事項:**
- このスクリプトを実行する前に、企業データが存在している必要があります
- メールアドレスはユニーク制約があるため、既存ユーザーと重複する場合はエラーになります
- 重複を避けるには `--clear` オプションを使用してください

---

## 実行例

### 初回セットアップ（完全なデータセット）

```bash
# 1. データベースマイグレーション
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/corporate_management_db" \
  alembic upgrade head

# 2. 完全なテストデータを投入
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/corporate_management_db" \
  DATABASE_URL_ASYNC="postgresql+asyncpg://postgres:postgres@localhost:5432/corporate_management_db" \
  python scripts/seed_test_data.py
```

### ユーザーデータのみを再投入

```bash
# 既存ユーザーをクリアして新しいユーザーを投入
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/corporate_management_db" \
  DATABASE_URL_ASYNC="postgresql+asyncpg://postgres:postgres@localhost:5432/corporate_management_db" \
  python scripts/seed_users.py --clear --yes
```

### 追加のユーザーを投入

```bash
# 既存ユーザーを保持したまま追加
# （メールアドレス重複に注意）
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/corporate_management_db" \
  DATABASE_URL_ASYNC="postgresql+asyncpg://postgres:postgres@localhost:5432/corporate_management_db" \
  python scripts/seed_users.py
```

---

## トラブルシューティング

### エラー: `企業データが存在しません`

`seed_users.py` を実行する前に、`seed_test_data.py` を実行して企業データを作成してください。

### エラー: `duplicate key value violates unique constraint "ix_users_email"`

既に同じメールアドレスのユーザーが存在しています。`--clear` オプションを使用して既存ユーザーをクリアしてから実行してください。

### パスワードハッシュの警告

```
(trapped) error reading bcrypt version
```

この警告は無害です。パスワードのハッシュ化は正常に動作しています。

---

## 権限システムについて

作成されるユーザーには、以下のグループロールが割り当てられます：

| グループ | コード | 説明 | 権限数 |
|---------|--------|------|--------|
| 管理者 | `admin` | システム全体の管理者 | 37権限（全権限） |
| マネージャー | `manager` | 部門の管理者 | 23権限 |
| 一般スタッフ | `staff` | 一般ユーザー | 12権限 |
| 閲覧者 | `viewer` | 閲覧のみ | 4権限 |

詳細は `claudedocs/API権限マッピング.md` を参照してください。

---

## データベース接続設定

スクリプトは以下の環境変数を使用します：

- `DATABASE_URL`: 同期接続用（Alembic等）
- `DATABASE_URL_ASYNC`: 非同期接続用（AsyncPG）

**例:**
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/corporate_management_db"
export DATABASE_URL_ASYNC="postgresql+asyncpg://postgres:postgres@localhost:5432/corporate_management_db"
```

または `.env` ファイルに設定することもできます。
