"""
ユーザーデータ投入スクリプト

既存の企業・支店データを前提として、テストユーザーを投入します。

使い方:
  python scripts/seed_users.py [--clear] [--yes]

オプション:
  --clear: 既存のユーザーデータをクリアしてから投入
  --yes: 確認をスキップして実行
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# backend ディレクトリをPythonパスに追加
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from app.config import get_settings
from app.models import (
    Company,
    User,
    GroupRole,
    UserGroupAssignment,
)

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def clear_users(session: AsyncSession):
    """既存のユーザーデータをクリア"""
    print("\n=== 既存ユーザーデータのクリア ===")

    # UserGroupAssignmentを先に削除（外部キー制約のため）
    result = await session.execute(delete(UserGroupAssignment))
    deleted_assignments = result.rowcount
    print(f"+ UserGroupAssignment削除: {deleted_assignments} 件")

    # Userを削除
    result = await session.execute(delete(User))
    deleted_users = result.rowcount
    print(f"+ User削除: {deleted_users} 件")

    await session.commit()
    print("クリア完了\n")


async def seed_users(clear_existing: bool = False):
    """ユーザーデータを投入"""
    # データベース接続
    engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("=" * 60)
            print("ユーザーデータ投入開始")
            print("=" * 60)

            # 既存データをクリア（オプション）
            if clear_existing:
                await clear_users(session)

            # ========================================
            # 1. 企業データ取得
            # ========================================
            print("\n=== 企業データ取得 ===")
            result = await session.execute(select(Company))
            companies = result.scalars().all()

            if not companies:
                print("❌ エラー: 企業データが存在しません。先に企業データを投入してください。")
                return

            print(f"+ {len(companies)} 社の企業データを取得")
            for company in companies:
                print(f"  - {company.name} (ID: {company.id})")

            # ========================================
            # 2. グループロール取得
            # ========================================
            print("\n=== グループロール取得 ===")

            # adminグループ取得
            result = await session.execute(
                select(GroupRole).where(GroupRole.code == "admin")
            )
            admin_group = result.scalar_one()
            print(f"+ adminグループ (ID: {admin_group.id})")

            # managerグループ取得
            result = await session.execute(
                select(GroupRole).where(GroupRole.code == "manager")
            )
            manager_group = result.scalar_one()
            print(f"+ managerグループ (ID: {manager_group.id})")

            # staffグループ取得
            result = await session.execute(
                select(GroupRole).where(GroupRole.code == "staff")
            )
            staff_group = result.scalar_one()
            print(f"+ staffグループ (ID: {staff_group.id})")

            # viewerグループ取得
            result = await session.execute(
                select(GroupRole).where(GroupRole.code == "viewer")
            )
            viewer_group = result.scalar_one_or_none()
            print(f"+ viewerグループ (ID: {viewer_group.id if viewer_group else 'なし'})")

            # ========================================
            # 3. ユーザーデータ定義
            # ========================================
            print("\n=== ユーザー作成 ===")

            # 最初の企業用のユーザー
            company_1_users = [
                {
                    "name": "システム管理者",
                    "email": f"admin@company{companies[0].id}.example.com",
                    "password": "admin123",
                    "role": "システム管理者",
                    "position": "社長",
                    "group_role": admin_group,
                    "description": "全権限を持つシステム管理者",
                },
                {
                    "name": "営業部長",
                    "email": f"sales-manager@company{companies[0].id}.example.com",
                    "password": "password123",
                    "role": "マネージャー",
                    "position": "部長",
                    "group_role": manager_group,
                    "description": "営業部門の責任者",
                },
                {
                    "name": "営業担当A",
                    "email": f"sales-a@company{companies[0].id}.example.com",
                    "password": "password123",
                    "role": "営業",
                    "position": "一般社員",
                    "group_role": staff_group,
                    "description": "営業担当スタッフ",
                },
                {
                    "name": "営業担当B",
                    "email": f"sales-b@company{companies[0].id}.example.com",
                    "password": "password123",
                    "role": "営業",
                    "position": "一般社員",
                    "group_role": staff_group,
                    "description": "営業担当スタッフ",
                },
                {
                    "name": "総務担当",
                    "email": f"general-affairs@company{companies[0].id}.example.com",
                    "password": "password123",
                    "role": "総務",
                    "position": "一般社員",
                    "group_role": staff_group,
                    "description": "総務担当スタッフ",
                },
            ]

            # 2社目以降の企業用のユーザー（存在する場合）
            other_companies_users = []
            for i, company in enumerate(companies[1:], start=1):
                other_companies_users.extend([
                    {
                        "company_id": company.id,
                        "name": f"管理者{i}",
                        "email": f"admin@company{company.id}.example.com",
                        "password": "password123",
                        "role": "管理者",
                        "position": "マネージャー",
                        "group_role": manager_group,
                        "description": f"{company.name}の管理者",
                    },
                    {
                        "company_id": company.id,
                        "name": f"スタッフ{i}-1",
                        "email": f"staff{i}-1@company{company.id}.example.com",
                        "password": "password123",
                        "role": "スタッフ",
                        "position": "一般社員",
                        "group_role": staff_group,
                        "description": f"{company.name}のスタッフ",
                    },
                    {
                        "company_id": company.id,
                        "name": f"スタッフ{i}-2",
                        "email": f"staff{i}-2@company{company.id}.example.com",
                        "password": "password123",
                        "role": "スタッフ",
                        "position": "一般社員",
                        "group_role": staff_group,
                        "description": f"{company.name}のスタッフ",
                    },
                ])

            # 全ユーザーデータを統合
            all_users_data = []

            # 最初の企業のユーザーを追加
            for user_data in company_1_users:
                user_data["company_id"] = companies[0].id
                all_users_data.append(user_data)

            # その他の企業のユーザーを追加
            all_users_data.extend(other_companies_users)

            # ========================================
            # 4. ユーザー作成とグループ割り当て
            # ========================================
            users_created = []

            for user_data in all_users_data:
                group_role = user_data.pop("group_role")
                password = user_data.pop("password")
                description = user_data.pop("description")

                # ユーザー作成
                user = User(
                    **user_data,
                    password_hash=pwd_context.hash(password)
                )
                session.add(user)
                await session.flush()

                # グループロール割り当て
                user_group = UserGroupAssignment(
                    user_id=user.id,
                    group_role_id=group_role.id,
                    assigned_at=datetime.now(),
                )
                session.add(user_group)

                users_created.append({
                    "user": user,
                    "group": group_role,
                    "email": user_data["email"],
                    "description": description,
                })

                company = next(c for c in companies if c.id == user.company_id)
                print(f"+ {user.name} ({user_data['email']}) - {group_role.name} @ {company.name}")

            await session.commit()
            print(f"\nユーザー作成完了: {len(users_created)} 名")

            # ========================================
            # 完了サマリー
            # ========================================
            print("\n" + "=" * 60)
            print("✅ ユーザーデータ投入完了！")
            print("=" * 60)

            print("\n【作成サマリー】")
            print(f"  総ユーザー数: {len(users_created)} 名")

            # グループ別カウント
            group_counts = {}
            for item in users_created:
                group_name = item["group"].name
                group_counts[group_name] = group_counts.get(group_name, 0) + 1

            print("\n【グループ別内訳】")
            for group_name, count in group_counts.items():
                print(f"  {group_name}: {count} 名")

            # 企業別カウント
            company_counts = {}
            for item in users_created:
                company = next(c for c in companies if c.id == item["user"].company_id)
                company_counts[company.name] = company_counts.get(company.name, 0) + 1

            print("\n【企業別内訳】")
            for company_name, count in company_counts.items():
                print(f"  {company_name}: {count} 名")

            print("\n【ログイン情報】")
            for item in users_created:
                company = next(c for c in companies if c.id == item["user"].company_id)
                password = "admin123" if item["group"].code == "admin" else "password123"
                role_mark = " ★全権限" if item["group"].code == "admin" else ""
                print(f"  {item['user'].name}: {item['email']} / {password}{role_mark}")
                print(f"    ({item['description']} @ {company.name})")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    # コマンドライン引数の処理
    clear_existing = "--clear" in sys.argv
    skip_confirm = "--yes" in sys.argv

    if clear_existing and not skip_confirm:
        print("\n⚠️  既存のユーザーデータをクリアして投入します")
        try:
            print("続行しますか? [y/N]: ", end="")
            response = input().strip().lower()
            if response != "y":
                print("中止しました")
                sys.exit(0)
        except EOFError:
            print("\n自動実行モード: 確認をスキップするには --yes フラグを使用してください")
            sys.exit(1)

    asyncio.run(seed_users(clear_existing=clear_existing))
