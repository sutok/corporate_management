# branches.py 権限適用例

**Before/After 比較**: ハードコードされたロールチェックから権限システムへの移行

---

## 📋 現状の問題点

### ❌ Before（現在のコード）

```python
@router.post("", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    branch: BranchCreate,
    current_user: User = Depends(get_current_user),  # ← 認証のみ
    db: AsyncSession = Depends(get_db),
):
    """支店作成（管理者のみ）"""
    # ❌ 問題1: ハードコードされたロール名
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    # ❌ 問題2: 企業チェックとビジネスロジックが混在
    if branch.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他の企業の支店は作成できません",
        )

    new_branch = Branch(**branch.model_dump())
    db.add(new_branch)
    await db.commit()
    await db.refresh(new_branch)
    return new_branch
```

**問題点**:
1. ❌ `"admin", "manager"` がハードコード
2. ❌ 権限変更時に全エンドポイントを修正が必要
3. ❌ GET系エンドポイントに権限チェックがない
4. ❌ ビジネスロジックと権限チェックが混在

---

## ✅ 改善版（権限システム適用後）

### ステップ1: importを追加

```python
"""
Branch API Router
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.branch import Branch
from app.models.user import User
from app.schemas.branch import BranchCreate, BranchUpdate, BranchResponse
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_permission  # ← 追加

router = APIRouter(prefix="/api/branches", tags=["branches"])
```

---

### ステップ2: GET系エンドポイントに権限追加

#### GET /api/branches（一覧取得）

```python
@router.get("", response_model=List[BranchResponse])
async def get_branches(
    skip: int = 0,
    limit: int = 100,
    # ✅ 変更: 権限チェックを追加
    current_user: User = Depends(require_permission("branch.view")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店一覧取得

    必要な権限: branch.view
    """
    result = await db.execute(
        select(Branch)
        .where(Branch.company_id == current_user.company_id)
        .offset(skip)
        .limit(limit)
    )
    branches = result.scalars().all()
    return branches
```

**変更点**:
- ✅ `get_current_user` → `require_permission("branch.view")`
- ✅ 権限がない場合は自動的に403エラー
- ✅ ドキュメントに必要な権限を明記

---

#### GET /api/branches/{branch_id}（詳細取得）

```python
@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: int,
    # ✅ 変更: 権限チェックを追加
    current_user: User = Depends(require_permission("branch.view")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店詳細取得

    必要な権限: branch.view
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支店が見つかりません",
        )

    # ✅ 変更なし: 企業レベルのアクセス制御は維持
    if branch.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    return branch
```

**変更点**:
- ✅ `get_current_user` → `require_permission("branch.view")`
- ✅ 企業レベルのチェックは引き続き維持（重要！）

---

### ステップ3: POST/PUT/DELETE の権限チェックを置き換え

#### POST /api/branches（作成）

```python
@router.post("", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    branch: BranchCreate,
    # ✅ 変更: require_permission で権限チェック
    current_user: User = Depends(require_permission("branch.create")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店作成

    必要な権限: branch.create
    """
    # ❌ 削除: ハードコードされたロールチェックを削除
    # if current_user.role not in ["admin", "manager"]:
    #     raise HTTPException(...)

    # ✅ 変更なし: 企業レベルのチェックは維持
    if branch.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他の企業の支店は作成できません",
        )

    new_branch = Branch(**branch.model_dump())
    db.add(new_branch)
    await db.commit()
    await db.refresh(new_branch)
    return new_branch
```

**変更点**:
- ✅ ハードコードされたロールチェックを削除
- ✅ `require_permission("branch.create")` で宣言的に権限指定
- ✅ コードが10行短くなった
- ✅ 企業レベルのチェックは維持

---

#### PUT /api/branches/{branch_id}（更新）

```python
@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: int,
    branch_update: BranchUpdate,
    # ✅ 変更: require_permission で権限チェック
    current_user: User = Depends(require_permission("branch.update")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店更新

    必要な権限: branch.update
    """
    # ❌ 削除: ハードコードされたロールチェックを削除
    # if current_user.role not in ["admin", "manager"]:
    #     raise HTTPException(...)

    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支店が見つかりません",
        )

    # ✅ 変更なし: 企業レベルのチェックは維持
    if branch.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    update_data = branch_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)

    await db.commit()
    await db.refresh(branch)
    return branch
```

---

#### DELETE /api/branches/{branch_id}（削除）

```python
@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(
    branch_id: int,
    # ✅ 変更: require_permission で権限チェック
    current_user: User = Depends(require_permission("branch.delete")),
    db: AsyncSession = Depends(get_db),
):
    """
    支店削除

    必要な権限: branch.delete
    """
    # ❌ 削除: ハードコードされたロールチェックを削除
    # if current_user.role not in ["admin", "manager"]:
    #     raise HTTPException(...)

    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支店が見つかりません",
        )

    # ✅ 変更なし: 企業レベルのチェックは維持
    if branch.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    await db.delete(branch)
    await db.commit()
```

---

## 📊 変更サマリー

### コード量の削減

| 項目 | Before | After | 削減 |
|------|--------|-------|------|
| GET一覧 | 権限チェックなし | `require_permission` | - |
| GET詳細 | 権限チェックなし | `require_permission` | - |
| POST | 7行のチェックコード | 1行のDependency | -6行 |
| PUT | 7行のチェックコード | 1行のDependency | -6行 |
| DELETE | 7行のチェックコード | 1行のDependency | -6行 |
| **合計** | **155行** | **135行** | **-20行** |

### 改善点

1. ✅ **宣言的**: 各エンドポイントの必要権限が一目でわかる
2. ✅ **保守性**: 権限変更時に1箇所の修正で済む
3. ✅ **一貫性**: 全エンドポイントで同じパターン
4. ✅ **テスタビリティ**: 権限テストが書きやすい
5. ✅ **ドキュメント**: 自動生成されるSwaggerに権限情報が含まれる

---

## 🔑 権限とシステムグループのマッピング

| 権限 | admin | manager | staff | viewer |
|------|-------|---------|-------|--------|
| `branch.view` | ✅ | ✅ | ✅ | ✅ |
| `branch.create` | ✅ | ❌ | ❌ | ❌ |
| `branch.update` | ✅ | ❌ | ❌ | ❌ |
| `branch.delete` | ✅ | ❌ | ❌ | ❌ |

**結果**:
- **admin**: 全操作可能
- **manager**: 閲覧のみ
- **staff**: 閲覧のみ
- **viewer**: 閲覧のみ

---

## 🧪 テストケース例

```python
# tests/test_branches.py

async def test_get_branches_without_permission(client, db):
    """権限がない場合は403エラー"""
    # ユーザーに権限を付与しない
    user = await create_test_user(db, permissions=[])
    token = create_access_token(user.id)

    response = client.get(
        "/api/branches",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert "権限が不足しています" in response.json()["detail"]


async def test_get_branches_with_permission(client, db):
    """branch.view権限がある場合は成功"""
    # ユーザーに権限を付与
    user = await create_test_user(db, permissions=["branch.view"])
    token = create_access_token(user.id)

    response = client.get(
        "/api/branches",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


async def test_create_branch_without_permission(client, db):
    """branch.create権限がない場合は403エラー"""
    user = await create_test_user(db, permissions=["branch.view"])
    token = create_access_token(user.id)

    response = client.post(
        "/api/branches",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "新宿支店", "company_id": user.company_id}
    )

    assert response.status_code == 403
```

---

## 💡 次のステップ

1. **branches.py を実際に更新**
2. **departments.py に同じパターンを適用**
3. **companies.py に同じパターンを適用**
4. **テストケースを追加**

全体で **2-3時間** の作業量です。

このパターンを理解すれば、他のルーターも同様に更新できます！
