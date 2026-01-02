"""
権限とシステムロールの初期データ投入スクリプト
"""
import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.config import get_settings
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

settings = get_settings()


# 権限定義
PERMISSIONS = [
    # Service 管理
    {
        "code": "service.view",
        "name": "サービス閲覧",
        "description": "サービス情報を閲覧する",
        "resource_type": "service",
    },
    {
        "code": "service.subscribe",
        "name": "サービス契約",
        "description": "サービスを契約する",
        "resource_type": "service",
    },
    {
        "code": "service.unsubscribe",
        "name": "サービス解約",
        "description": "サービスを解約する",
        "resource_type": "service",
    },
    {
        "code": "service.manage",
        "name": "サービス管理",
        "description": "サービス設定を管理する",
        "resource_type": "service",
    },
    # Subscription 管理
    {
        "code": "subscription.view",
        "name": "契約状況閲覧",
        "description": "自社の契約状況を閲覧する",
        "resource_type": "subscription",
    },
    {
        "code": "subscription.history",
        "name": "契約履歴閲覧",
        "description": "契約履歴を閲覧する",
        "resource_type": "subscription",
    },
    # User 管理
    {
        "code": "user.view",
        "name": "ユーザー閲覧",
        "description": "ユーザー情報を閲覧する",
        "resource_type": "user",
    },
    {
        "code": "user.create",
        "name": "ユーザー作成",
        "description": "新しいユーザーを作成する",
        "resource_type": "user",
    },
    {
        "code": "user.update",
        "name": "ユーザー更新",
        "description": "ユーザー情報を更新する",
        "resource_type": "user",
    },
    {
        "code": "user.delete",
        "name": "ユーザー削除",
        "description": "ユーザーを削除する",
        "resource_type": "user",
    },
    {
        "code": "user.view_self",
        "name": "自分の情報閲覧",
        "description": "自分のユーザー情報を閲覧する",
        "resource_type": "user",
    },
    # Company 管理
    {
        "code": "company.view",
        "name": "企業情報閲覧",
        "description": "企業情報を閲覧する",
        "resource_type": "company",
    },
    {
        "code": "company.update",
        "name": "企業情報更新",
        "description": "企業情報を更新する",
        "resource_type": "company",
    },
    {
        "code": "company.delete",
        "name": "企業削除",
        "description": "企業を削除する",
        "resource_type": "company",
    },
    # Report 管理
    {
        "code": "report.view",
        "name": "レポート閲覧",
        "description": "レポートを閲覧する",
        "resource_type": "report",
    },
    {
        "code": "report.view_all",
        "name": "全レポート閲覧",
        "description": "全てのレポートを閲覧する",
        "resource_type": "report",
    },
    {
        "code": "report.create",
        "name": "レポート作成",
        "description": "新しいレポートを作成する",
        "resource_type": "report",
    },
    {
        "code": "report.update_own",
        "name": "自分のレポート更新",
        "description": "自分のレポートを更新する",
        "resource_type": "report",
    },
    {
        "code": "report.approve",
        "name": "レポート承認",
        "description": "レポートを承認する",
        "resource_type": "report",
    },
    # Role 管理
    {
        "code": "role.view",
        "name": "ロール閲覧",
        "description": "ロール情報を閲覧する",
        "resource_type": "role",
    },
    {
        "code": "role.create",
        "name": "ロール作成",
        "description": "新しいロールを作成する",
        "resource_type": "role",
    },
    {
        "code": "role.update",
        "name": "ロール更新",
        "description": "ロール情報を更新する",
        "resource_type": "role",
    },
    {
        "code": "role.delete",
        "name": "ロール削除",
        "description": "ロールを削除する",
        "resource_type": "role",
    },
    {
        "code": "role.assign",
        "name": "ロール割り当て",
        "description": "ユーザーにロールを割り当てる",
        "resource_type": "role",
    },
]


# システムロール定義
SYSTEM_ROLES = [
    {
        "code": "super_admin",
        "name": "システム管理者",
        "description": "システム全体の管理者。すべての権限を持つ",
        "permissions": "*",  # すべての権限
    },
    {
        "code": "company_admin",
        "name": "企業管理者",
        "description": "企業の管理者。ユーザー管理、サービス契約を行う",
        "permissions": [
            "user.view",
            "user.create",
            "user.update",
            "user.delete",
            "company.view",
            "company.update",
            "service.view",
            "service.subscribe",
            "service.unsubscribe",
            "subscription.view",
            "subscription.history",
            "report.view_all",
            "role.view",
            "role.assign",
        ],
    },
    {
        "code": "subscription_manager",
        "name": "サービス管理者",
        "description": "サービス契約の管理を行う",
        "permissions": [
            "service.view",
            "service.subscribe",
            "service.unsubscribe",
            "service.manage",
            "subscription.view",
            "subscription.history",
        ],
    },
    {
        "code": "report_viewer",
        "name": "レポート閲覧者",
        "description": "レポートの閲覧権限を持つ",
        "permissions": [
            "report.view",
            "subscription.view",
        ],
    },
    {
        "code": "basic_user",
        "name": "一般ユーザー",
        "description": "基本的なユーザー権限",
        "permissions": [
            "report.create",
            "report.update_own",
            "user.view_self",
            "report.view",
        ],
    },
]


async def seed_permissions_and_roles():
    """権限とロールの初期データを投入"""
    # データベース接続
    engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # 1. 権限を作成
            print("\n=== 権限の作成 ===")
            permission_map = {}
            for perm_data in PERMISSIONS:
                # 既存チェック
                result = await session.execute(
                    select(Permission).where(Permission.code == perm_data["code"])
                )
                existing = result.scalar_one_or_none()

                if existing:
                    print(f"✓ 既存: {perm_data['code']}")
                    permission_map[perm_data["code"]] = existing
                else:
                    permission = Permission(**perm_data)
                    session.add(permission)
                    await session.flush()
                    permission_map[perm_data["code"]] = permission
                    print(f"+ 作成: {perm_data['code']}")

            await session.commit()
            print(f"\n権限作成完了: {len(permission_map)} 件")

            # 2. システムロールを作成
            print("\n=== システムロールの作成 ===")
            for role_data in SYSTEM_ROLES:
                # 既存チェック
                result = await session.execute(
                    select(Role).where(
                        Role.code == role_data["code"], Role.company_id.is_(None)
                    )
                )
                existing_role = result.scalar_one_or_none()

                if existing_role:
                    print(f"✓ 既存: {role_data['code']}")
                    role = existing_role
                else:
                    role = Role(
                        company_id=None,  # システムロール
                        code=role_data["code"],
                        name=role_data["name"],
                        description=role_data["description"],
                        is_system=True,
                    )
                    session.add(role)
                    await session.flush()
                    print(f"+ 作成: {role_data['code']}")

                # 権限を割り当て
                if role_data["permissions"] == "*":
                    # すべての権限を割り当て
                    perms_to_assign = list(permission_map.values())
                else:
                    # 指定された権限のみ
                    perms_to_assign = [
                        permission_map[code] for code in role_data["permissions"]
                    ]

                # 既存の権限割り当てをチェック
                for perm in perms_to_assign:
                    result = await session.execute(
                        select(RolePermission).where(
                            RolePermission.role_id == role.id,
                            RolePermission.permission_id == perm.id,
                        )
                    )
                    existing_rp = result.scalar_one_or_none()

                    if not existing_rp:
                        role_perm = RolePermission(role_id=role.id, permission_id=perm.id)
                        session.add(role_perm)

                print(f"  → 権限割り当て: {len(perms_to_assign)} 件")

            await session.commit()
            print(f"\nシステムロール作成完了: {len(SYSTEM_ROLES)} 件")

            print("\n✅ 初期データ投入完了！")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ エラー: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_permissions_and_roles())
