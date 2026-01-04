"""
テストデータ投入スクリプト

組織系:
- 2企業（東京商事、大阪物産）
- 各企業に2支店
- 各支店に1部署
- ユーザー5名
  - 東京商事: システム管理者(全権限)、一般スタッフ、マネージャー
  - 大阪物産: 一般スタッフ、マネージャー

サービス系:
- 組織管理サービス
- 日報管理サービス
"""
import asyncio
import sys
from pathlib import Path

# backend ディレクトリをPythonパスに追加
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import date, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from app.config import get_settings
from app.models import (
    Company,
    Branch,
    Department,
    User,
    Service,
    CompanyServiceSubscription,
    GroupRole,
    UserGroupAssignment,
)

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_test_data():
    """テストデータを投入"""
    # データベース接続
    engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("=" * 60)
            print("テストデータ投入開始")
            print("=" * 60)

            # ========================================
            # 1. 企業作成（2社）
            # ========================================
            print("\n=== 企業の作成 ===")

            companies_data = [
                {
                    "name": "東京商事株式会社",
                    "address": "東京都千代田区丸の内1-1-1",
                    "phone": "03-1234-5678",
                },
                {
                    "name": "大阪物産株式会社",
                    "address": "大阪府大阪市北区梅田2-2-2",
                    "phone": "06-9876-5432",
                },
            ]

            companies = []
            for company_data in companies_data:
                company = Company(**company_data)
                session.add(company)
                await session.flush()
                companies.append(company)
                print(f"+ 作成: {company.name} (ID: {company.id})")

            await session.commit()
            print(f"企業作成完了: {len(companies)} 社")

            # ========================================
            # 2. 支店・部署作成（各企業に2支店、各支店に1部署）
            # ========================================
            print("\n=== 支店・部署の作成 ===")

            branches_data = [
                # 東京商事の支店
                {
                    "company_id": companies[0].id,
                    "name": "東京本社",
                    "address": "東京都千代田区丸の内1-1-1",
                    "phone": "03-1234-5678",
                },
                {
                    "company_id": companies[0].id,
                    "name": "横浜支店",
                    "address": "神奈川県横浜市西区みなとみらい3-3-3",
                    "phone": "045-1234-5678",
                },
                # 大阪物産の支店
                {
                    "company_id": companies[1].id,
                    "name": "大阪本社",
                    "address": "大阪府大阪市北区梅田2-2-2",
                    "phone": "06-9876-5432",
                },
                {
                    "company_id": companies[1].id,
                    "name": "神戸支店",
                    "address": "兵庫県神戸市中央区三宮町4-4-4",
                    "phone": "078-9876-5432",
                },
            ]

            branches = []
            for branch_data in branches_data:
                branch = Branch(**branch_data)
                session.add(branch)
                await session.flush()
                branches.append(branch)
                company = next(c for c in companies if c.id == branch.company_id)
                print(f"+ 作成支店: {branch.name} (企業: {company.name})")

            await session.commit()

            departments_data = [
                # 東京本社の部署
                {
                    "branch_id": branches[0].id,
                    "name": "営業部",
                    "description": "営業活動を担当",
                },
                # 横浜支店の部署
                {
                    "branch_id": branches[1].id,
                    "name": "営業部",
                    "description": "営業活動を担当",
                },
                # 大阪本社の部署
                {
                    "branch_id": branches[2].id,
                    "name": "営業部",
                    "description": "営業活動を担当",
                },
                # 神戸支店の部署
                {
                    "branch_id": branches[3].id,
                    "name": "営業部",
                    "description": "営業活動を担当",
                },
            ]

            departments = []
            for dept_data in departments_data:
                dept = Department(**dept_data)
                session.add(dept)
                await session.flush()
                departments.append(dept)
                branch = next(b for b in branches if b.id == dept.branch_id)
                print(f"+ 作成部署: {dept.name} (支店: {branch.name})")

            await session.commit()
            print(f"支店・部署作成完了: {len(branches)} 支店, {len(departments)} 部署")

            # ========================================
            # 3. グループロール取得
            # ========================================
            print("\n=== グループロール取得 ===")

            # adminグループ取得
            result = await session.execute(
                select(GroupRole).where(GroupRole.code == "admin")
            )
            admin_group = result.scalar_one()
            print(f"+ adminグループ取得 (ID: {admin_group.id})")

            # managerグループ取得
            result = await session.execute(
                select(GroupRole).where(GroupRole.code == "manager")
            )
            manager_group = result.scalar_one()
            print(f"+ managerグループ取得 (ID: {manager_group.id})")

            # staffグループ取得
            result = await session.execute(
                select(GroupRole).where(GroupRole.code == "staff")
            )
            staff_group = result.scalar_one()
            print(f"+ staffグループ取得 (ID: {staff_group.id})")

            # ========================================
            # 4. ユーザー作成（各支店に1名）
            # ========================================
            print("\n=== ユーザーの作成 ===")

            users_data = [
                # 東京商事 - 東京本社（システム管理者）
                {
                    "company_id": companies[0].id,
                    "name": "管理者太郎",
                    "email": "admin@tokyo-shoji.co.jp",
                    "password": "admin123",
                    "role": "システム管理者",
                    "position": "社長",
                    "group_role": admin_group,
                    "branch_name": "東京本社",
                },
                # 東京商事 - 東京本社（一般ユーザー）
                {
                    "company_id": companies[0].id,
                    "name": "山田太郎",
                    "email": "yamada@tokyo-shoji.co.jp",
                    "password": "password123",
                    "role": "営業",
                    "position": "一般社員",
                    "group_role": staff_group,
                    "branch_name": "東京本社",
                },
                # 東京商事 - 横浜支店（マネージャー）
                {
                    "company_id": companies[0].id,
                    "name": "佐藤花子",
                    "email": "sato@tokyo-shoji.co.jp",
                    "password": "password123",
                    "role": "マネージャー",
                    "position": "部長",
                    "group_role": manager_group,
                    "branch_name": "横浜支店",
                },
                # 大阪物産 - 大阪本社（一般ユーザー）
                {
                    "company_id": companies[1].id,
                    "name": "鈴木一郎",
                    "email": "suzuki@osaka-bussan.co.jp",
                    "password": "password123",
                    "role": "営業",
                    "position": "一般社員",
                    "group_role": staff_group,
                    "branch_name": "大阪本社",
                },
                # 大阪物産 - 神戸支店（マネージャー）
                {
                    "company_id": companies[1].id,
                    "name": "田中美咲",
                    "email": "tanaka@osaka-bussan.co.jp",
                    "password": "password123",
                    "role": "マネージャー",
                    "position": "部長",
                    "group_role": manager_group,
                    "branch_name": "神戸支店",
                },
            ]

            users = []
            for user_data in users_data:
                group_role = user_data.pop("group_role")
                password = user_data.pop("password")
                branch_name = user_data.pop("branch_name")

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

                users.append(user)
                company = next(c for c in companies if c.id == user.company_id)
                print(f"+ 作成: {user.name} ({user.email}) - {group_role.name} (企業: {company.name}, 支店: {branch_name})")

            await session.commit()
            print(f"ユーザー作成完了: {len(users)} 名")

            # ========================================
            # 5. サービス作成
            # ========================================
            print("\n=== サービスの作成 ===")

            services_data = [
                {
                    "service_code": "ORGANIZATION_MANAGEMENT",
                    "service_name": "組織管理サービス",
                    "description": "企業、支店、部署、ユーザーの管理機能を提供",
                    "base_price": 10000.00,
                    "is_active": True,
                },
                {
                    "service_code": "DAILY_REPORT",
                    "service_name": "日報管理サービス",
                    "description": "営業日報の作成、閲覧、管理機能を提供",
                    "base_price": 5000.00,
                    "is_active": True,
                },
            ]

            services = []
            for service_data in services_data:
                service = Service(**service_data)
                session.add(service)
                await session.flush()
                services.append(service)
                print(f"+ 作成: {service.service_name} (コード: {service.service_code}, 基本料金: ¥{service.base_price:,.0f})")

            await session.commit()
            print(f"サービス作成完了: {len(services)} 件")

            # ========================================
            # 6. サービス契約（全企業が全サービスを契約）
            # ========================================
            print("\n=== サービス契約の作成 ===")

            subscriptions = []
            for company in companies:
                for service in services:
                    subscription = CompanyServiceSubscription(
                        company_id=company.id,
                        service_id=service.id,
                        status="active",
                        start_date=date.today(),
                        monthly_price=service.base_price,
                    )
                    session.add(subscription)
                    await session.flush()
                    subscriptions.append(subscription)
                    print(f"+ 契約: {company.name} → {service.service_name} (月額: ¥{subscription.monthly_price:,.0f})")

            await session.commit()
            print(f"サービス契約完了: {len(subscriptions)} 件")

            # ========================================
            # 完了
            # ========================================
            print("\n" + "=" * 60)
            print("✅ テストデータ投入完了！")
            print("=" * 60)
            print("\n【作成サマリー】")
            print(f"  企業: {len(companies)} 社")
            print(f"  支店: {len(branches)} 支店")
            print(f"  部署: {len(departments)} 部署")
            print(f"  ユーザー: {len(users)} 名")
            print(f"  サービス: {len(services)} 件")
            print(f"  契約: {len(subscriptions)} 件")
            print("\n【ログイン情報】")
            print("  東京商事:")
            print("    東京本社 (システム管理者): admin@tokyo-shoji.co.jp / admin123 ★全権限")
            print("    東京本社 (一般スタッフ): yamada@tokyo-shoji.co.jp / password123")
            print("    横浜支店 (マネージャー): sato@tokyo-shoji.co.jp / password123")
            print("  大阪物産:")
            print("    大阪本社 (一般スタッフ): suzuki@osaka-bussan.co.jp / password123")
            print("    神戸支店 (マネージャー): tanaka@osaka-bussan.co.jp / password123")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_test_data())
