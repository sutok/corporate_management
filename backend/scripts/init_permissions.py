"""
権限システム初期化スクリプト

GroupRole（グループ）とPermission（権限）の初期データを投入します。
このスクリプトはマイグレーション後、テストデータ投入前に実行する必要があります。

使い方:
  python scripts/init_permissions.py
"""
import asyncio
import sys
from pathlib import Path

# backend ディレクトリをPythonパスに追加
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models import GroupRole, Role, GroupRolePermission

settings = get_settings()


async def init_permissions():
    """権限システムを初期化"""
    engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("=" * 60)
            print("権限システム初期化開始")
            print("=" * 60)

            # ========================================
            # 1. GroupRole 作成
            # ========================================
            print("\n=== グループロール作成 ===")

            # 既存のグループを確認
            result = await session.execute(select(GroupRole))
            existing_groups = {g.code: g for g in result.scalars().all()}

            groups_data = [
                {
                    "code": "admin",
                    "name": "管理者",
                    "description": "システム全体の管理者。全ての権限を持つ。",
                    "is_system": True,
                },
                {
                    "code": "manager",
                    "name": "マネージャー",
                    "description": "部門の管理者。部門内のデータを管理できる。",
                    "is_system": True,
                },
                {
                    "code": "staff",
                    "name": "一般スタッフ",
                    "description": "一般ユーザー。自分のデータと閲覧権限のあるデータにアクセスできる。",
                    "is_system": True,
                },
                {
                    "code": "viewer",
                    "name": "閲覧者",
                    "description": "閲覧のみ可能。データの変更はできない。",
                    "is_system": True,
                },
            ]

            groups = {}
            for group_data in groups_data:
                if group_data["code"] in existing_groups:
                    group = existing_groups[group_data["code"]]
                    print(f"  既存: {group.name} ({group.code})")
                else:
                    group = GroupRole(**group_data)
                    session.add(group)
                    await session.flush()
                    print(f"+ 作成: {group.name} ({group.code})")

                groups[group.code] = group

            await session.commit()
            print(f"グループロール: {len(groups)} 件")

            # ========================================
            # 2. Role (Permission) 作成
            # ========================================
            print("\n=== 権限作成 ===")

            # 既存の権限を確認
            result = await session.execute(select(Role))
            existing_permissions = {p.code: p for p in result.scalars().all()}

            permissions_data = [
                # 支店管理
                {"code": "branch.view", "name": "支店閲覧", "resource_type": "branch", "description": "支店情報を閲覧"},
                {"code": "branch.create", "name": "支店作成", "resource_type": "branch", "description": "新しい支店を作成"},
                {"code": "branch.update", "name": "支店更新", "resource_type": "branch", "description": "支店情報を更新"},
                {"code": "branch.delete", "name": "支店削除", "resource_type": "branch", "description": "支店を削除"},

                # 企業管理
                {"code": "company.view", "name": "企業閲覧", "resource_type": "company", "description": "企業情報を閲覧"},
                {"code": "company.update", "name": "企業更新", "resource_type": "company", "description": "企業情報を更新"},

                # 顧客管理
                {"code": "customer.view", "name": "顧客閲覧", "resource_type": "customer", "description": "顧客情報を閲覧"},
                {"code": "customer.create", "name": "顧客作成", "resource_type": "customer", "description": "新しい顧客を作成"},
                {"code": "customer.update", "name": "顧客更新", "resource_type": "customer", "description": "顧客情報を更新"},
                {"code": "customer.delete", "name": "顧客削除", "resource_type": "customer", "description": "顧客を削除"},

                # 部署管理
                {"code": "department.view", "name": "部署閲覧", "resource_type": "department", "description": "部署情報を閲覧"},
                {"code": "department.create", "name": "部署作成", "resource_type": "department", "description": "新しい部署を作成"},
                {"code": "department.update", "name": "部署更新", "resource_type": "department", "description": "部署情報を更新"},
                {"code": "department.delete", "name": "部署削除", "resource_type": "department", "description": "部署を削除"},

                # 日報管理
                {"code": "report.view_all", "name": "日報全件閲覧", "resource_type": "report", "description": "全ての日報を閲覧"},
                {"code": "report.view_self", "name": "日報自分のみ閲覧", "resource_type": "report", "description": "自分の日報のみ閲覧"},
                {"code": "report.create", "name": "日報作成", "resource_type": "report", "description": "日報を作成"},
                {"code": "report.update_self", "name": "日報自分のみ更新", "resource_type": "report", "description": "自分の日報のみ更新"},
                {"code": "report.delete_self", "name": "日報自分のみ削除", "resource_type": "report", "description": "自分の日報のみ削除"},
                {"code": "report.approve", "name": "日報承認", "resource_type": "report", "description": "日報を承認"},

                # サービス管理
                {"code": "service.view", "name": "サービス閲覧", "resource_type": "service", "description": "サービス情報を閲覧"},
                {"code": "service.create", "name": "サービス作成", "resource_type": "service", "description": "新しいサービスを作成"},
                {"code": "service.update", "name": "サービス更新", "resource_type": "service", "description": "サービス情報を更新"},
                {"code": "service.delete", "name": "サービス削除", "resource_type": "service", "description": "サービスを削除"},

                # サービス契約管理
                {"code": "subscription.view", "name": "契約閲覧", "resource_type": "subscription", "description": "契約情報を閲覧"},
                {"code": "subscription.create", "name": "契約作成", "resource_type": "subscription", "description": "新しい契約を作成"},
                {"code": "subscription.update", "name": "契約更新", "resource_type": "subscription", "description": "契約情報を更新"},
                {"code": "subscription.delete", "name": "契約削除", "resource_type": "subscription", "description": "契約を削除"},

                # ユーザー管理
                {"code": "user.view", "name": "ユーザー閲覧", "resource_type": "user", "description": "ユーザー情報を閲覧"},
                {"code": "user.create", "name": "ユーザー作成", "resource_type": "user", "description": "新しいユーザーを作成"},
                {"code": "user.update", "name": "ユーザー更新", "resource_type": "user", "description": "ユーザー情報を更新"},
                {"code": "user.update_self", "name": "ユーザー自分のみ更新", "resource_type": "user", "description": "自分の情報のみ更新"},
                {"code": "user.delete", "name": "ユーザー削除", "resource_type": "user", "description": "ユーザーを削除"},

                # ユーザー割り当て管理
                {"code": "user_assignment.view", "name": "ユーザー割り当て閲覧", "resource_type": "user_assignment", "description": "ユーザー割り当てを閲覧"},
                {"code": "user_assignment.create", "name": "ユーザー割り当て作成", "resource_type": "user_assignment", "description": "ユーザー割り当てを作成"},
                {"code": "user_assignment.delete", "name": "ユーザー割り当て削除", "resource_type": "user_assignment", "description": "ユーザー割り当てを削除"},
            ]

            permissions = {}
            for perm_data in permissions_data:
                if perm_data["code"] in existing_permissions:
                    perm = existing_permissions[perm_data["code"]]
                else:
                    perm = Role(**perm_data)
                    session.add(perm)
                    await session.flush()

                permissions[perm.code] = perm

            await session.commit()
            print(f"権限: {len(permissions)} 件作成")

            # ========================================
            # 3. GroupPermission 割り当て
            # ========================================
            print("\n=== グループ権限割り当て ===")

            # 既存の割り当てを確認
            result = await session.execute(select(GroupRolePermission))
            existing_assignments = {
                (gp.group_role_id, gp.role_id): gp
                for gp in result.scalars().all()
            }

            # 管理者: 全権限
            admin_permissions = list(permissions.values())

            # マネージャー: 閲覧全般 + 一部作成・更新
            manager_permissions = [
                permissions[code] for code in [
                    "branch.view", "branch.create", "branch.update",
                    "company.view",
                    "customer.view", "customer.create", "customer.update",
                    "department.view", "department.create", "department.update",
                    "report.view_all", "report.create", "report.update_self", "report.approve",
                    "service.view",
                    "subscription.view", "subscription.create", "subscription.update",
                    "user.view", "user.create", "user.update", "user.update_self",
                    "user_assignment.view", "user_assignment.create", "user_assignment.delete",
                ]
            ]

            # スタッフ: 閲覧と自分のデータ操作
            staff_permissions = [
                permissions[code] for code in [
                    "branch.view",
                    "company.view",
                    "customer.view", "customer.create", "customer.update",
                    "department.view",
                    "report.view_self", "report.create", "report.update_self", "report.delete_self",
                    "service.view",
                    "subscription.view",
                    "user.view", "user.update_self",
                ]
            ]

            # 閲覧者: 閲覧のみ
            viewer_permissions = [
                permissions[code] for code in [
                    "branch.view",
                    "company.view",
                    "customer.view",
                    "department.view",
                    "report.view_self",
                    "service.view",
                    "subscription.view",
                    "user.view",
                ]
            ]

            assignments = [
                (groups["admin"], admin_permissions),
                (groups["manager"], manager_permissions),
                (groups["staff"], staff_permissions),
                (groups["viewer"], viewer_permissions),
            ]

            total_assigned = 0
            for group, perms in assignments:
                assigned_count = 0
                for perm in perms:
                    key = (group.id, perm.id)
                    if key not in existing_assignments:
                        gp = GroupRolePermission(
                            group_role_id=group.id,
                            role_id=perm.id,
                        )
                        session.add(gp)
                        assigned_count += 1

                total_assigned += assigned_count
                print(f"+ {group.name}: {len(perms)} 権限 (新規: {assigned_count})")

            await session.commit()
            print(f"グループ権限割り当て: {total_assigned} 件")

            # ========================================
            # 完了サマリー
            # ========================================
            print("\n" + "=" * 60)
            print("✅ 権限システム初期化完了！")
            print("=" * 60)
            print("\n【作成サマリー】")
            print(f"  グループロール: {len(groups)} 件")
            print(f"  権限: {len(permissions)} 件")
            print(f"  グループ権限割り当て: 合計 {sum(len(p) for _, p in assignments)} 件")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_permissions())
