"""
データベースリセットスクリプト（psqlコマンド不要）

このスクリプトは psql コマンドを使わずに、
Pythonから直接PostgreSQLデータベースをリセットします。

使い方:
  python scripts/reset_database.py [--yes]

オプション:
  --yes: 確認をスキップして実行
"""
import asyncio
import sys
from pathlib import Path

# backend ディレクトリをPythonパスに追加
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings

settings = get_settings()


def parse_database_url(url: str) -> dict:
    """データベースURLをパース"""
    # postgresql://user:pass@host:port/dbname
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "")
    elif url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "")

    # user:pass@host:port/dbname
    if "@" in url:
        credentials, location = url.split("@", 1)
        user, password = credentials.split(":", 1) if ":" in credentials else (credentials, "")
    else:
        user, password = "postgres", ""
        location = url

    # host:port/dbname
    if "/" in location:
        host_port, dbname = location.split("/", 1)
    else:
        host_port, dbname = location, "postgres"

    if ":" in host_port:
        host, port = host_port.split(":", 1)
        port = int(port)
    else:
        host, port = host_port, 5432

    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database": dbname,
    }


async def drop_database(db_config: dict, target_db: str):
    """データベースを削除"""
    # postgresデータベースに接続して対象データベースを削除
    conn = await asyncpg.connect(
        user=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"],
        database="postgres",  # デフォルトのpostgresデータベースに接続
    )

    try:
        # 既存の接続を切断
        await conn.execute(
            f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{target_db}'
              AND pid <> pg_backend_pid();
            """
        )

        # データベース削除
        await conn.execute(f'DROP DATABASE IF EXISTS "{target_db}"')
        print(f"✓ データベース削除完了: {target_db}")

    finally:
        await conn.close()


async def create_database(db_config: dict, target_db: str):
    """データベースを作成"""
    conn = await asyncpg.connect(
        user=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"],
        database="postgres",
    )

    try:
        await conn.execute(f'CREATE DATABASE "{target_db}"')
        print(f"✓ データベース作成完了: {target_db}")

    finally:
        await conn.close()


def run_migrations():
    """Alembicマイグレーションを実行"""
    import subprocess

    print("\nマイグレーション実行中...")
    result = subprocess.run(
        [".venv/bin/alembic", "upgrade", "head"],
        env={
            **subprocess.os.environ,
            "DATABASE_URL": settings.DATABASE_URL,
        },
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✓ マイグレーション完了")
    else:
        print(f"✗ マイグレーション失敗:\n{result.stderr}")
        raise Exception("マイグレーション失敗")


def run_init_permissions():
    """権限システムを初期化"""
    import subprocess

    print("\n権限システム初期化中...")
    result = subprocess.run(
        [".venv/bin/python", "scripts/init_permissions.py"],
        env={
            **subprocess.os.environ,
            "DATABASE_URL": settings.DATABASE_URL,
            "DATABASE_URL_ASYNC": settings.DATABASE_URL_ASYNC,
        },
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✓ 権限システム初期化完了")
    else:
        print(f"✗ 権限システム初期化失敗:\n{result.stderr}")
        raise Exception("権限システム初期化失敗")


def run_seed():
    """テストデータを投入"""
    import subprocess

    print("\nテストデータ投入中...")
    result = subprocess.run(
        [".venv/bin/python", "scripts/seed_test_data.py"],
        env={
            **subprocess.os.environ,
            "DATABASE_URL": settings.DATABASE_URL,
            "DATABASE_URL_ASYNC": settings.DATABASE_URL_ASYNC,
        },
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✓ テストデータ投入完了")
        # サマリー部分だけ表示
        for line in result.stdout.split("\n"):
            if any(
                keyword in line
                for keyword in [
                    "作成サマリー",
                    "企業:",
                    "支店:",
                    "部署:",
                    "ユーザー:",
                    "サービス:",
                    "契約:",
                    "ログイン情報",
                    "★全権限",
                ]
            ):
                print(line)
    else:
        print(f"✗ テストデータ投入失敗:\n{result.stderr}")
        raise Exception("テストデータ投入失敗")


async def reset_database(skip_confirm: bool = False):
    """データベースをリセット"""
    try:
        print("=" * 60)
        print("データベースリセット")
        print("=" * 60)

        # データベース設定を解析
        db_config = parse_database_url(settings.DATABASE_URL)
        target_db = db_config["database"]

        print(f"\nデータベース: {target_db}")
        print(f"ホスト: {db_config['host']}:{db_config['port']}")
        print(f"ユーザー: {db_config['user']}")

        if not skip_confirm:
            print("\n⚠️  全てのデータが削除されます。続行しますか? [y/N]: ", end="")
            try:
                response = input().strip().lower()
                if response != "y":
                    print("中止しました")
                    return
            except EOFError:
                print("\n確認をスキップするには --yes フラグを使用してください")
                return

        print("\n" + "=" * 60)
        print("処理開始")
        print("=" * 60)

        # 1. データベース削除
        print("\n[1/4] データベース削除中...")
        await drop_database(db_config, target_db)

        # 2. データベース作成
        print("\n[2/4] データベース作成中...")
        await create_database(db_config, target_db)

        # 3. マイグレーション実行
        print("\n[3/5] マイグレーション実行中...")
        run_migrations()

        # 4. 権限システム初期化
        print("\n[4/5] 権限システム初期化中...")
        run_init_permissions()

        # 5. テストデータ投入
        print("\n[5/5] テストデータ投入中...")
        run_seed()

        print("\n" + "=" * 60)
        print("✅ データベースリセット完了！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    skip_confirm = "--yes" in sys.argv

    asyncio.run(reset_database(skip_confirm=skip_confirm))
