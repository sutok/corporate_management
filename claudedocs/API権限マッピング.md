# APIエンドポイントと権限コードのマッピング

**作成日**: 2026-01-04
**バージョン**: 1.0

このドキュメントは、各APIエンドポイントで要求される権限コードの完全なマッピングを提供します。

---

## 📋 目次

1. [エンドポイント一覧](#エンドポイント一覧)
2. [権限コード命名規則](#権限コード命名規則)
3. [権限チェックパターン](#権限チェックパターン)
4. [実装参照](#実装参照)

---

## エンドポイント一覧

### BRANCHES (支店管理)

| Method | Endpoint | Permission Code | 説明 |
|--------|----------|-----------------|------|
| GET | /api/branches | `branch.view` | 支店一覧取得 |
| GET | /api/branches/{branch_id} | `branch.view` | 支店詳細取得 |
| POST | /api/branches | `branch.create` | 支店作成 |
| PUT | /api/branches/{branch_id} | `branch.update` | 支店更新 |
| DELETE | /api/branches/{branch_id} | `branch.delete` | 支店削除 |

**実装**: `backend/app/routers/branches.py`

---

### COMPANIES (企業管理)

| Method | Endpoint | Permission Code | 説明 |
|--------|----------|-----------------|------|
| GET | /api/companies | `company.view` | 企業一覧取得 |
| GET | /api/companies/{company_id} | `company.view` | 企業詳細取得 |
| POST | /api/companies | `company.create` | 企業作成 |
| PUT | /api/companies/{company_id} | `company.update` | 企業更新 |
| DELETE | /api/companies/{company_id} | `company.delete` | 企業削除 |

**実装**: `backend/app/routers/companies.py`

---

### CUSTOMERS (顧客管理)

| Method | Endpoint | Permission Code | 説明 |
|--------|----------|-----------------|------|
| GET | /api/customers | `customer.view` | 顧客一覧取得 |
| GET | /api/customers/{customer_id} | `customer.view` | 顧客詳細取得 |
| POST | /api/customers | `customer.create` | 顧客作成 |
| PUT | /api/customers/{customer_id} | `customer.update` | 顧客更新 |
| DELETE | /api/customers/{customer_id} | `customer.delete` | 顧客削除 |

**実装**: `backend/app/routers/customers.py`

---

### DAILY_REPORTS (日報管理)

| Method | Endpoint | Permission Code | 説明 |
|--------|----------|-----------------|------|
| GET | /api/daily-reports | `report.view_all` OR `report.view_self` | 日報一覧取得 |
| GET | /api/daily-reports/{report_id} | `report.view_all` OR `report.view_self` | 日報詳細取得 |
| POST | /api/daily-reports | `report.create` | 日報作成 |
| PUT | /api/daily-reports/{report_id} | `report.update` OR `report.update_self` | 日報更新 |
| DELETE | /api/daily-reports/{report_id} | `report.delete` OR `report.delete_self` | 日報削除 |

**実装**: `backend/app/routers/daily_reports.py`

**特記事項**:
- 動的スコープを採用（Pattern 3）
- 自分の日報のみ操作可能なユーザーと、全員の日報を操作可能なユーザーを区別

---

### DEPARTMENTS (部署管理)

| Method | Endpoint | Permission Code | 説明 |
|--------|----------|-----------------|------|
| GET | /api/departments | `department.view` | 部署一覧取得 |
| GET | /api/departments/{department_id} | `department.view` | 部署詳細取得 |
| POST | /api/departments | `department.create` | 部署作成 |
| PUT | /api/departments/{department_id} | `department.update` | 部署更新 |
| DELETE | /api/departments/{department_id} | `department.delete` | 部署削除 |

**実装**: `backend/app/routers/departments.py`

---

### USERS (ユーザー管理)

| Method | Endpoint | Permission Code | 説明 |
|--------|----------|-----------------|------|
| GET | /api/users | `user.view` | ユーザー一覧取得 |
| GET | /api/users/{user_id} | `user.view` | ユーザー詳細取得 |
| POST | /api/users | `user.create` | ユーザー作成 |
| PUT | /api/users/{user_id} | `user.update` OR `user.update_self` | ユーザー更新 |
| DELETE | /api/users/{user_id} | `user.delete` | ユーザー削除 |

**実装**: `backend/app/routers/users.py`

**特記事項**:
- 自己更新パターンを採用（Pattern 2）
- 自分のプロフィール更新は `user.update_self` で可能
- 他ユーザーの更新には `user.update` が必要

---

### SUBSCRIPTIONS (サービス契約管理)

| Method | Endpoint | Permission Code | 説明 |
|--------|----------|-----------------|------|
| GET | /api/subscriptions | `subscription.view` | サービス契約一覧取得 |
| GET | /api/subscriptions/history | `subscription.history` | サービス契約履歴取得 |
| POST | /api/subscriptions/{service_id}/subscribe | `service.subscribe` | サービス契約 |
| POST | /api/subscriptions/{subscription_id}/unsubscribe | `service.unsubscribe` | サービス契約解除 |
| GET | /api/subscriptions/services | `service.view` OR `subscription.view` | サービス一覧取得 |

**実装**: `backend/app/routers/subscriptions.py`

---

## 権限コード命名規則

### 基本パターン

```
<resource>.<action>
```

### Resource (リソース)

| Code | 日本語 | 説明 |
|------|--------|------|
| `branch` | 支店 | 企業配下の支店情報 |
| `company` | 企業 | 企業マスタ情報 |
| `customer` | 顧客 | 顧客情報 |
| `report` | 日報 | 営業日報データ |
| `department` | 部署 | 支店配下の部署情報 |
| `user` | ユーザー | システムユーザー情報 |
| `service` | サービス | オプションサービス |
| `subscription` | サービス契約 | 企業のサービス契約情報 |

### Action (操作)

| Code | 日本語 | 説明 |
|------|--------|------|
| `view` | 閲覧 | リソースの閲覧権限 |
| `view_all` | 全件閲覧 | 全ユーザーのリソースを閲覧可能 |
| `view_self` | 自分のみ閲覧 | 自分が作成したリソースのみ閲覧可能 |
| `create` | 作成 | 新規リソースの作成権限 |
| `update` | 更新 | リソースの更新権限 |
| `update_self` | 自分のみ更新 | 自分が作成したリソースのみ更新可能 |
| `delete` | 削除 | リソースの削除権限 |
| `delete_self` | 自分のみ削除 | 自分が作成したリソースのみ削除可能 |
| `subscribe` | 契約 | サービス契約権限 |
| `unsubscribe` | 契約解除 | サービス契約解除権限 |
| `history` | 履歴閲覧 | 変更履歴の閲覧権限 |

### 権限コード例

```python
# 基本的なCRUD権限
"branch.view"     # 支店閲覧
"branch.create"   # 支店作成
"branch.update"   # 支店更新
"branch.delete"   # 支店削除

# スコープ付き権限
"report.view_all"      # 全員の日報を閲覧
"report.view_self"     # 自分の日報のみ閲覧
"user.update"          # 他ユーザーの情報を更新
"user.update_self"     # 自分の情報のみ更新
```

---

## 権限チェックパターン

### Pattern 1: 単一権限（Basic CRUD）

最もシンプルなパターン。エンドポイントアクセスに1つの特定権限が必要。

**使用例**: branches, companies, departments

**実装**:
```python
@router.get("", response_model=List[BranchResponse])
async def get_branches(
    current_user: User = Depends(require_permission("branch.view")),
    db: AsyncSession = Depends(get_db),
):
    """支店一覧取得 - branch.view 権限が必要"""
    ...
```

**適用ルーター**:
- `branches.py` - 全エンドポイント
- `companies.py` - 全エンドポイント
- `departments.py` - 全エンドポイント

---

### Pattern 2: 自己操作許可（Self-Operation）

自分のデータ操作と他人のデータ操作で異なる権限を要求。いずれかの権限があればアクセス可能。

**使用例**: users, customers

**実装**:
```python
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_any_permission(["user.update", "user.update_self"])),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザー更新
    - 他ユーザー更新: user.update
    - 自己更新: user.update_self
    """
    # 実行時チェック
    if user_id != current_user.id:
        check_permission(current_user, "user.update")
    ...
```

**適用ルーター**:
- `users.py` - PUT /api/users/{user_id}
- `customers.py` - PUT /api/customers/{customer_id}, DELETE /api/customers/{customer_id}

**権限の組み合わせ**:
- `user.update` OR `user.update_self`
- `customer.update` OR `customer.update_self`
- `customer.delete` OR `customer.delete_self`

---

### Pattern 3: 動的スコープ（Dynamic Scope）

データの所有者判定を実行時に行い、スコープに応じた権限チェックを実施。

**使用例**: daily_reports

**実装**:
```python
@router.get("", response_model=List[DailyReportResponse])
async def get_daily_reports(
    current_user: User = Depends(require_any_permission(["report.view_all", "report.view_self"])),
    db: AsyncSession = Depends(get_db),
):
    """
    日報一覧取得
    - 全件閲覧: report.view_all
    - 自分のみ: report.view_self
    """
    # 権限に応じてデータフィルタリング
    query = select(DailyReport).where(DailyReport.company_id == current_user.company_id)

    if not check_permission(current_user, "report.view_all"):
        # view_self しか持っていない場合は自分のデータのみ
        query = query.where(DailyReport.user_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().all()
```

**適用ルーター**:
- `daily_reports.py` - 全エンドポイント

**権限の組み合わせ**:
- `report.view_all` OR `report.view_self`
- `report.update` OR `report.update_self`
- `report.delete` OR `report.delete_self`

**動的フィルタリング**:
```python
# view_all 権限がある場合: 全データ取得
# view_self 権限のみの場合: user_id でフィルタリング

if not check_permission(current_user, "report.view_all"):
    query = query.where(DailyReport.user_id == current_user.id)
```

---

## 実装参照

### 権限チェック関数

**場所**: `backend/app/auth/permissions.py`

#### require_permission
```python
def require_permission(permission_code: str) -> User:
    """
    単一権限チェック (Pattern 1)
    指定された権限を持っていない場合は 403 Forbidden
    """
```

#### require_any_permission
```python
def require_any_permission(permission_codes: list[str]) -> User:
    """
    複数権限チェック（OR条件） (Pattern 2, 3)
    いずれか1つの権限があればアクセス許可
    """
```

#### check_permission
```python
async def check_permission(user: User, permission_code: str, db: AsyncSession) -> bool:
    """
    権限確認（例外を投げない）
    実行時の動的チェックに使用 (Pattern 3)
    """
```

### ルーター実装

| Router | File | Patterns Used |
|--------|------|---------------|
| Branches | `backend/app/routers/branches.py` | Pattern 1 |
| Companies | `backend/app/routers/companies.py` | Pattern 1 |
| Departments | `backend/app/routers/departments.py` | Pattern 1 |
| Users | `backend/app/routers/users.py` | Pattern 2 |
| Customers | `backend/app/routers/customers.py` | Pattern 2 |
| Daily Reports | `backend/app/routers/daily_reports.py` | Pattern 3 |
| Subscriptions | `backend/app/routers/subscriptions.py` | Pattern 1 |

### 詳細ドキュメント

- 権限システム全体設計: `claudedocs/権限管理.md`
- 権限適用例: `backend/claudedocs/branches_権限適用例.md`
- 権限割り当て戦略: `backend/claudedocs/権限割り当て戦略.md`

---

## まとめ

### 権限コード総数

**37個の権限コード**が定義されています（`backend/scripts/seed_permissions.py` 参照）

### パターン別分類

- **Pattern 1 (Basic CRUD)**: 20権限
  - branch.* (5), company.* (5), department.* (5), subscription.* (5)

- **Pattern 2 (Self-Operation)**: 9権限
  - user.* (5), customer.* (4)

- **Pattern 3 (Dynamic Scope)**: 8権限
  - report.* (8)

### グループ定義

**4つのシステムグループ**:
- `admin` - システム管理者（全権限）
- `manager` - マネージャー（view_all権限あり）
- `staff` - 一般スタッフ（基本権限）
- `viewer` - 閲覧専用（view権限のみ）

詳細は `backend/scripts/seed_permissions.py` を参照。

---

**最終更新**: 2026-01-04
**管理**: Claude Code
