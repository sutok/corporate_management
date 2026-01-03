# Makefile for Corporate Management System
# Docker Compose management commands

.PHONY: help up down build restart ps logs clean dev test db-migrate db-seed db-shell

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)Corporate Management System - Docker Compose Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Docker Compose Operations

up: ## Start all services
	@echo "$(GREEN)Starting all services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Services started successfully!$(NC)"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo "PgAdmin: http://localhost:5050"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker compose down
	@echo "$(GREEN)Services stopped successfully!$(NC)"

build: ## Build or rebuild services
	@echo "$(BLUE)Building services...$(NC)"
	docker compose build
	@echo "$(GREEN)Build completed!$(NC)"

rebuild: ## Rebuild services without cache
	@echo "$(BLUE)Rebuilding services (no cache)...$(NC)"
	docker compose build --no-cache
	@echo "$(GREEN)Rebuild completed!$(NC)"

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	docker compose restart
	@echo "$(GREEN)Services restarted!$(NC)"

ps: ## Show running services
	@docker compose ps

##@ Service-Specific Operations

up-db: ## Start only database service
	@echo "$(GREEN)Starting database...$(NC)"
	docker compose up -d postgres

up-backend: ## Start backend service (with dependencies)
	@echo "$(GREEN)Starting backend...$(NC)"
	docker compose up -d backend

up-frontend: ## Start frontend service (with dependencies)
	@echo "$(GREEN)Starting frontend...$(NC)"
	docker compose up -d frontend

restart-backend: ## Restart backend service
	@echo "$(YELLOW)Restarting backend...$(NC)"
	docker compose restart backend

restart-frontend: ## Restart frontend service
	@echo "$(YELLOW)Restarting frontend...$(NC)"
	docker compose restart frontend

##@ Logs

logs: ## Show logs for all services
	docker compose logs -f

logs-backend: ## Show backend logs
	docker compose logs -f backend

logs-frontend: ## Show frontend logs
	docker compose logs -f frontend

logs-db: ## Show database logs
	docker compose logs -f postgres

logs-pgadmin: ## Show pgadmin logs
	docker compose logs -f pgadmin

##@ Database Operations

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	docker compose exec backend alembic upgrade head
	@echo "$(GREEN)Migrations completed!$(NC)"

db-migrate-create: ## Create a new migration (usage: make db-migrate-create MSG="description")
	@echo "$(BLUE)Creating new migration...$(NC)"
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)Migration file created!$(NC)"

db-seed: ## Seed database with initial data
	@echo "$(BLUE)Seeding database...$(NC)"
	docker compose exec backend python scripts/seed_permissions.py
	@echo "$(GREEN)Database seeded successfully!$(NC)"

db-shell: ## Access PostgreSQL shell
	@echo "$(BLUE)Connecting to database...$(NC)"
	docker compose exec postgres psql -U postgres -d corporate_management_db

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(YELLOW)Resetting database...$(NC)"; \
		docker compose down -v; \
		docker compose up -d postgres; \
		sleep 5; \
		docker compose exec backend alembic upgrade head; \
		docker compose exec backend python scripts/seed_permissions.py; \
		echo "$(GREEN)Database reset completed!$(NC)"; \
	else \
		echo "$(GREEN)Cancelled.$(NC)"; \
	fi

##@ Development

dev: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker compose up -d
	@echo ""
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Frontend: http://localhost:5173"
	@echo "PgAdmin: http://localhost:5050 (admin@corporate_management.local / admin)"
	@echo ""
	@echo "To view logs: make logs"

shell-backend: ## Access backend container shell
	@docker compose exec backend /bin/bash

shell-db: ## Access database container shell
	@docker compose exec postgres /bin/bash

##@ Testing

test: ## Run backend tests
	@echo "$(BLUE)Running tests...$(NC)"
	docker compose exec backend pytest -v
	@echo "$(GREEN)Tests completed!$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	docker compose exec backend pytest --cov=app --cov-report=term-missing -v
	@echo "$(GREEN)Coverage report generated!$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	docker compose exec backend pytest -v --looponfail

##@ Cleanup

clean: ## Stop services and remove containers
	@echo "$(YELLOW)Cleaning up containers...$(NC)"
	docker compose down
	@echo "$(GREEN)Cleanup completed!$(NC)"

clean-all: ## Remove containers, volumes, and images
	@echo "$(RED)WARNING: This will remove all containers, volumes, and images!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(YELLOW)Removing everything...$(NC)"; \
		docker compose down -v --rmi all; \
		echo "$(GREEN)Everything removed!$(NC)"; \
	else \
		echo "$(GREEN)Cancelled.$(NC)"; \
	fi

clean-volumes: ## Remove volumes only
	@echo "$(YELLOW)Removing volumes...$(NC)"
	docker compose down -v
	@echo "$(GREEN)Volumes removed!$(NC)"

##@ Health Check

health: ## Check health status of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo ""
	@docker compose ps
	@echo ""
	@echo "$(BLUE)Database connection test...$(NC)"
	@docker compose exec postgres pg_isready -U postgres || echo "$(RED)Database not ready$(NC)"
	@echo ""
	@echo "$(BLUE)Backend health check...$(NC)"
	@curl -s http://localhost:8000/health > /dev/null && echo "$(GREEN)Backend is healthy$(NC)" || echo "$(RED)Backend not responding$(NC)"

status: ## Show detailed status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(BLUE)Docker Stats:$(NC)"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
