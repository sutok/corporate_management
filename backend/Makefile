.PHONY: help install dev test lint format clean db-reset db-migrate db-seed db-seed-users db-shell

# デフォルトのデータベース接続設定
DB_NAME ?= corporate_management_db
DB_USER ?= postgres
DB_PASS ?= postgres
DB_HOST ?= localhost
DB_PORT ?= 5432

# 環境変数
export DATABASE_URL = postgresql://$(DB_USER):$(DB_PASS)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)
export DATABASE_URL_ASYNC = postgresql+asyncpg://$(DB_USER):$(DB_PASS)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)
export SECRET_KEY = your-secret-key-change-this-in-production

# Pythonバイナリ
PYTHON = .venv/bin/python
PIP = .venv/bin/pip
PYTEST = .venv/bin/pytest
ALEMBIC = .venv/bin/alembic

help: ## ヘルプを表示
	@echo "利用可能なコマンド:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 依存関係をインストール
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

dev: ## 開発サーバーを起動
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## テストを実行
	$(PYTEST) tests/ -v

test-cov: ## カバレッジ付きでテストを実行
	$(PYTEST) tests/ -v --cov=app --cov-report=html --cov-report=term

lint: ## コードのlintチェック
	$(PYTHON) -m flake8 app/ tests/
	$(PYTHON) -m mypy app/

format: ## コードをフォーマット
	$(PYTHON) -m black app/ tests/
	$(PYTHON) -m isort app/ tests/

clean: ## 一時ファイルを削除
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov

# データベース操作

db-reset: ## データベースをリセット（全削除→マイグレーション→シード）
	@if command -v psql >/dev/null 2>&1; then \
		echo "⚠️  データベースをリセットします: $(DB_NAME)"; \
		echo "全てのデータが削除されます。続行しますか? [y/N] " && read ans && [ $${ans:-N} = y ]; \
		echo "データベース削除中..."; \
		psql -h $(DB_HOST) -U $(DB_USER) -c "DROP DATABASE IF EXISTS $(DB_NAME);" || true; \
		echo "データベース作成中..."; \
		psql -h $(DB_HOST) -U $(DB_USER) -c "CREATE DATABASE $(DB_NAME);"; \
		echo "マイグレーション実行中..."; \
		$(MAKE) db-migrate; \
		echo "テストデータ投入中..."; \
		$(MAKE) db-seed; \
		echo "✅ データベースリセット完了！"; \
	else \
		echo "psqlコマンドが見つかりません。Pythonスクリプトを使用します..."; \
		$(PYTHON) scripts/reset_database.py; \
	fi

db-reset-auto: ## データベースを確認なしでリセット（CI用）
	@if command -v psql >/dev/null 2>&1; then \
		echo "データベース削除中..."; \
		psql -h $(DB_HOST) -U $(DB_USER) -c "DROP DATABASE IF EXISTS $(DB_NAME);" || true; \
		echo "データベース作成中..."; \
		psql -h $(DB_HOST) -U $(DB_USER) -c "CREATE DATABASE $(DB_NAME);"; \
		echo "マイグレーション実行中..."; \
		$(MAKE) db-migrate; \
		echo "テストデータ投入中..."; \
		$(MAKE) db-seed; \
		echo "✅ データベースリセット完了！"; \
	else \
		echo "psqlコマンドが見つかりません。Pythonスクリプトを使用します..."; \
		$(PYTHON) scripts/reset_database.py --yes; \
	fi

db-migrate: ## マイグレーションを実行
	$(ALEMBIC) upgrade head

db-migrate-create: ## 新しいマイグレーションファイルを作成
	@read -p "マイグレーション名: " name; \
	$(ALEMBIC) revision --autogenerate -m "$$name"

db-migrate-downgrade: ## マイグレーションを1つ戻す
	$(ALEMBIC) downgrade -1

db-migrate-history: ## マイグレーション履歴を表示
	$(ALEMBIC) history

db-migrate-current: ## 現在のマイグレーションバージョンを表示
	$(ALEMBIC) current

db-seed: ## 完全なテストデータを投入
	$(PYTHON) scripts/seed_test_data.py

db-seed-users: ## ユーザーデータのみを投入
	$(PYTHON) scripts/seed_users.py

db-seed-users-clear: ## ユーザーデータをクリアして投入
	$(PYTHON) scripts/seed_users.py --clear --yes

db-shell: ## PostgreSQLシェルを起動
	psql -h $(DB_HOST) -U $(DB_USER) -d $(DB_NAME)

db-status: ## データベース接続とマイグレーション状態を確認
	@echo "データベース接続確認..."
	@psql -h $(DB_HOST) -U $(DB_USER) -d $(DB_NAME) -c "SELECT version();" || echo "❌ 接続失敗"
	@echo "\n現在のマイグレーションバージョン:"
	@$(ALEMBIC) current

# Docker操作

docker-up: ## Dockerコンテナを起動
	docker-compose up -d

docker-down: ## Dockerコンテナを停止
	docker-compose down

docker-logs: ## Dockerログを表示
	docker-compose logs -f

docker-ps: ## 実行中のコンテナを表示
	docker-compose ps

# 開発用コマンド

shell: ## Pythonシェルを起動
	$(PYTHON)

routes: ## APIルート一覧を表示
	$(PYTHON) -c "from app.main import app; from fastapi.routing import APIRoute; routes = [route for route in app.routes if isinstance(route, APIRoute)]; [print(f'{route.methods} {route.path}') for route in sorted(routes, key=lambda x: x.path)]"

check: ## 全チェックを実行（lint + test）
	$(MAKE) lint
	$(MAKE) test

init: ## 初期セットアップ（install + db-reset）
	$(MAKE) install
	$(MAKE) db-reset
