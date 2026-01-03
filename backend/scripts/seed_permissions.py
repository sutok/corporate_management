#!/usr/bin/env python3
"""
Permission System Initial Data Seeder
権限管理システム初期データ投入スクリプト

このスクリプトは以下のデータを投入します:
1. 基本的な権限（roles）
2. システムグループ（group_roles）
3. グループと権限の関連付け（group_role_permissions）
"""
import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.models.role import Role
from app.models.group_role import GroupRole
from app.models.group_role_permission import GroupRolePermission
from app.config import get_settings


# 設定を取得
settings = get_settings()

# データベースエンジンを作成
engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=False,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# ========================================
# 権限定義
# ========================================

PERMISSIONS = [
    # ユーザー管理
    {"code": "user.view", "name": "ユーザー閲覧", "resource_type": "user", "description": "ユーザー情報を閲覧する権限"},
    {"code": "user.view_self", "name": "自分の情報閲覧", "resource_type": "user", "description": "自分のユーザー情報を閲覧する権限"},
    {"code": "user.create", "name": "ユーザー作成", "resource_type": "user", "description": "新しいユーザーを作成する権限"},
    {"code": "user.update", "name": "ユーザー更新", "resource_type": "user", "description": "ユーザー情報を更新する権限"},
    {"code": "user.update_self", "name": "自分の情報更新", "resource_type": "user", "description": "自分のユーザー情報を更新する権限"},
    {"code": "user.delete", "name": "ユーザー削除", "resource_type": "user", "description": "ユーザーを削除する権限"},

    # 日報管理
    {"code": "report.view", "name": "日報閲覧", "resource_type": "report", "description": "日報を閲覧する権限"},
    {"code": "report.view_all", "name": "全日報閲覧", "resource_type": "report", "description": "全ユーザーの日報を閲覧する権限"},
    {"code": "report.view_self", "name": "自分の日報閲覧", "resource_type": "report", "description": "自分の日報を閲覧する権限"},
    {"code": "report.create", "name": "日報作成", "resource_type": "report", "description": "日報を作成する権限"},
    {"code": "report.update", "name": "日報更新", "resource_type": "report", "description": "日報を更新する権限"},
    {"code": "report.update_self", "name": "自分の日報更新", "resource_type": "report", "description": "自分の日報を更新する権限"},
    {"code": "report.delete", "name": "日報削除", "resource_type": "report", "description": "日報を削除する権限"},
    {"code": "report.delete_self", "name": "自分の日報削除", "resource_type": "report", "description": "自分の日報を削除する権限"},
    {"code": "report.approve", "name": "日報承認", "resource_type": "report", "description": "日報を承認する権限"},
    {"code": "report.comment", "name": "日報コメント", "resource_type": "report", "description": "日報にコメントする権限"},

    # 顧客管理
    {"code": "customer.view", "name": "顧客閲覧", "resource_type": "customer", "description": "顧客情報を閲覧する権限"},
    {"code": "customer.view_assigned", "name": "担当顧客閲覧", "resource_type": "customer", "description": "自分が担当する顧客を閲覧する権限"},
    {"code": "customer.create", "name": "顧客作成", "resource_type": "customer", "description": "新しい顧客を作成する権限"},
    {"code": "customer.update", "name": "顧客更新", "resource_type": "customer", "description": "顧客情報を更新する権限"},
    {"code": "customer.delete", "name": "顧客削除", "resource_type": "customer", "description": "顧客を削除する権限"},

    # 企業管理
    {"code": "company.view", "name": "企業情報閲覧", "resource_type": "company", "description": "企業情報を閲覧する権限"},
    {"code": "company.create", "name": "企業作成", "resource_type": "company", "description": "新規企業を作成する権限（システム管理者専用）"},
    {"code": "company.update", "name": "企業情報更新", "resource_type": "company", "description": "企業情報を更新する権限"},
    {"code": "company.delete", "name": "企業削除", "resource_type": "company", "description": "企業を削除する権限（システム管理者専用、通常使用しない）"},

    # 支店・部署管理
    {"code": "branch.view", "name": "支店閲覧", "resource_type": "branch", "description": "支店情報を閲覧する権限"},
    {"code": "branch.create", "name": "支店作成", "resource_type": "branch", "description": "新しい支店を作成する権限"},
    {"code": "branch.update", "name": "支店更新", "resource_type": "branch", "description": "支店情報を更新する権限"},
    {"code": "branch.delete", "name": "支店削除", "resource_type": "branch", "description": "支店を削除する権限"},
    {"code": "department.view", "name": "部署閲覧", "resource_type": "department", "description": "部署情報を閲覧する権限"},
    {"code": "department.create", "name": "部署作成", "resource_type": "department", "description": "新しい部署を作成する権限"},
    {"code": "department.update", "name": "部署更新", "resource_type": "department", "description": "部署情報を更新する権限"},
    {"code": "department.delete", "name": "部署削除", "resource_type": "department", "description": "部署を削除する権限"},

    # 権限管理
    {"code": "permission.view", "name": "権限閲覧", "resource_type": "permission", "description": "権限情報を閲覧する権限"},
    {"code": "permission.assign", "name": "権限付与", "resource_type": "permission", "description": "ユーザーに権限を付与する権限"},
    {"code": "permission.revoke", "name": "権限剥奪", "resource_type": "permission", "description": "ユーザーから権限を剥奪する権限"},
    {"code": "permission.manage_groups", "name": "グループ管理", "resource_type": "permission", "description": "権限グループを管理する権限"},

    # システム管理
    {"code": "admin.access", "name": "管理画面アクセス", "resource_type": "admin", "description": "管理画面にアクセスする権限"},
    {"code": "admin.system_settings", "name": "システム設定", "resource_type": "admin", "description": "システム設定を変更する権限"},
]


# ========================================
# システムグループ定義
# ========================================

SYSTEM_GROUPS = [
    {
        "code": "admin",
        "name": "管理者",
        "description": "システム管理者。全ての権限を持つ",
        "permissions": [perm["code"] for perm in PERMISSIONS],  # 全権限
    },
    {
        "code": "manager",
        "name": "マネージャー",
        "description": "部門マネージャー。チームメンバーの日報確認と承認が可能",
        "permissions": [
            "user.view", "user.view_self", "user.update_self",
            "report.view_all", "report.view_self", "report.create", "report.update_self",
            "report.delete_self", "report.approve", "report.comment",
            "customer.view", "customer.view_assigned", "customer.create", "customer.update",
            "company.view",
            "branch.view", "department.view",
        ],
    },
    {
        "code": "staff",
        "name": "一般スタッフ",
        "description": "一般的な営業スタッフ。自分の日報管理と担当顧客管理が可能",
        "permissions": [
            "user.view_self", "user.update_self",
            "report.view_self", "report.create", "report.update_self", "report.delete_self",
            "customer.view_assigned", "customer.create", "customer.update",
            "company.view",
            "branch.view", "department.view",
        ],
    },
    {
        "code": "viewer",
        "name": "閲覧者",
        "description": "読み取り専用ユーザー。情報の閲覧のみ可能",
        "permissions": [
            "user.view_self",
            "report.view_self",
            "customer.view_assigned",
            "company.view",
            "branch.view", "department.view",
        ],
    },
]


async def seed_permissions():
    """権限データを投入"""
    async with async_session() as session:
        print("=" * 60)
        print("権限データ投入開始")
        print("=" * 60)

        # 既存の権限を確認
        result = await session.execute(select(Role))
        existing_roles = {role.code: role for role in result.scalars().all()}

        created_count = 0
        skipped_count = 0

        for perm_data in PERMISSIONS:
            if perm_data["code"] in existing_roles:
                print(f"⏭  スキップ: {perm_data['code']} （既に存在）")
                skipped_count += 1
                continue

            role = Role(**perm_data)
            session.add(role)
            print(f"✓ 追加: {perm_data['code']} - {perm_data['name']}")
            created_count += 1

        await session.commit()

        print(f"\n権限データ投入完了: 追加 {created_count}件, スキップ {skipped_count}件")
        print("=" * 60)


async def seed_system_groups():
    """システムグループデータを投入"""
    async with async_session() as session:
        print("\n" + "=" * 60)
        print("システムグループデータ投入開始")
        print("=" * 60)

        # 既存のグループを確認
        result = await session.execute(select(GroupRole).where(GroupRole.is_system == True))
        existing_groups = {group.code: group for group in result.scalars().all()}

        # 全権限を取得（グループとの関連付けに使用）
        result = await session.execute(select(Role))
        all_roles = {role.code: role for role in result.scalars().all()}

        created_count = 0
        skipped_count = 0

        for group_data in SYSTEM_GROUPS:
            if group_data["code"] in existing_groups:
                print(f"⏭  スキップ: {group_data['code']} （既に存在）")
                skipped_count += 1
                continue

            # グループを作成
            group = GroupRole(
                code=group_data["code"],
                name=group_data["name"],
                description=group_data["description"],
                company_id=None,  # システムグループ
                is_system=True,
            )
            session.add(group)
            await session.flush()  # IDを取得するためにflush

            # グループに権限を関連付け
            permission_count = 0
            for perm_code in group_data["permissions"]:
                if perm_code in all_roles:
                    group_perm = GroupRolePermission(
                        group_role_id=group.id,
                        role_id=all_roles[perm_code].id,
                    )
                    session.add(group_perm)
                    permission_count += 1

            print(f"✓ 追加: {group_data['code']} - {group_data['name']} （{permission_count}個の権限）")
            created_count += 1

        await session.commit()

        print(f"\nシステムグループデータ投入完了: 追加 {created_count}件, スキップ {skipped_count}件")
        print("=" * 60)


async def main():
    """メイン処理"""
    try:
        print("\n🚀 権限管理システム初期データ投入スクリプト")
        print(f"データベース: {settings.DATABASE_URL_ASYNC.split('@')[-1]}\n")

        # 1. 権限データを投入
        await seed_permissions()

        # 2. システムグループデータを投入
        await seed_system_groups()

        print("\n✅ 全ての初期データ投入が完了しました！\n")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
