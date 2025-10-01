.PHONY: help install dev build up down logs restart ps clean test lint format db-migrate db-rollback db-reset

# ════════════════════════════════════════════════════════════════════════════════
# Makefile for microservices project automation
# ════════════════════════════════════════════════════════════════════════════════

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default environment
ENV ?= dev
COMPOSE_FILE := docker-compose.yml
ifeq ($(ENV),dev)
	COMPOSE_FILE := docker-compose.yml -f docker-compose.dev.yml
else ifeq ($(ENV),prod)
	COMPOSE_FILE := docker-compose.yml -f docker-compose.prod.yml
endif

# ════════════════════════════════════════════════════════════════════════════════
# HELP
# ════════════════════════════════════════════════════════════════════════════════
help: ## Show this help message
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(GREEN)Microservices Project - Make Commands$(RESET)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Usage examples:$(RESET)"
	@echo "  make dev                  # Start development environment"
	@echo "  make ENV=prod up          # Start production environment"
	@echo "  make test                 # Run all tests"
	@echo "  make logs SERVICE=api     # Show logs for specific service"
	@echo ""

# ════════════════════════════════════════════════════════════════════════════════
# SETUP & INSTALLATION
# ════════════════════════════════════════════════════════════════════════════════
install: ## Install dependencies for all services
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	@for service in services/*; do \
		if [ -f "$$service/requirements.txt" ]; then \
			echo "$(BLUE)Installing $$service...$(RESET)"; \
			cd $$service && pip install -r requirements.txt && cd ../..; \
		fi \
	done
	@echo "$(GREEN)✓ Dependencies installed$(RESET)"

setup: ## Initial project setup
	@echo "$(GREEN)Setting up project...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env from .env.example$(RESET)"; \
		cp .env.example .env; \
		echo "$(YELLOW)⚠ Please edit .env file with your configuration$(RESET)"; \
	fi
	@mkdir -p services/{api_service,bot_service,worker_service,db_postgres_service,db_mongo_service}
	@mkdir -p nginx/certs nginx/conf.d
	@mkdir -p infrastructure/monitoring/{prometheus,grafana}
	@mkdir -p logs
	@echo "$(GREEN)✓ Project setup complete$(RESET)"

# ════════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT
# ════════════════════════════════════════════════════════════════════════════════
dev: ## Start development environment with hot reload
	@echo "$(GREEN)Starting development environment...$(RESET)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-detached: ## Start development environment in background
	@echo "$(GREEN)Starting development environment (detached)...$(RESET)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@$(MAKE) ps

# ════════════════════════════════════════════════════════════════════════════════
# DOCKER OPERATIONS
# ════════════════════════════════════════════════════════════════════════════════
build: ## Build all Docker images
	@echo "$(GREEN)Building Docker images...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) build
	@echo "$(GREEN)✓ Build complete$(RESET)"

build-no-cache: ## Build all Docker images without cache
	@echo "$(GREEN)Building Docker images (no cache)...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache

up: ## Start all services
	@echo "$(GREEN)Starting services...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@$(MAKE) ps

down: ## Stop all services
	@echo "$(YELLOW)Stopping services...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✓ Services stopped$(RESET)"

restart: ## Restart all services
	@echo "$(YELLOW)Restarting services...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✓ Services restarted$(RESET)"

ps: ## Show running services status
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(GREEN)Running Services:$(RESET)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) ps

logs: ## Show logs from all services (or specific: make logs SERVICE=api_service)
	@if [ -z "$(SERVICE)" ]; then \
		docker-compose -f $(COMPOSE_FILE) logs -f; \
	else \
		docker-compose -f $(COMPOSE_FILE) logs -f $(SERVICE); \
	fi

shell: ## Open shell in service container (make shell SERVICE=api_service)
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)Error: SERVICE not specified. Usage: make shell SERVICE=api_service$(RESET)"; \
	else \
		docker-compose -f $(COMPOSE_FILE) exec $(SERVICE) /bin/sh; \
	fi

# ════════════════════════════════════════════════════════════════════════════════
# TESTING
# ════════════════════════════════════════════════════════════════════════════════
test: ## Run all tests
	@echo "$(GREEN)Running all tests...$(RESET)"
	@for service in services/*; do \
		if [ -d "$$service/tests" ]; then \
			echo "$(BLUE)Testing $$service...$(RESET)"; \
			cd $$service && pytest tests/ -v --tb=short && cd ../..; \
		fi \
	done
	@echo "$(GREEN)✓ All tests passed$(RESET)"

test-cov: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(RESET)"
	@for service in services/*; do \
		if [ -d "$$service/tests" ]; then \
			echo "$(BLUE)Testing $$service with coverage...$(RESET)"; \
			cd $$service && \
			pytest tests/ --cov=src --cov-report=html --cov-report=term --cov-report=xml && \
			cd ../..; \
		fi \
	done
	@echo "$(GREEN)✓ Coverage reports generated in each service/htmlcov/$(RESET)"

test-service: ## Run tests for specific service (make test-service SERVICE=api_service)
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)Error: SERVICE not specified. Usage: make test-service SERVICE=api_service$(RESET)"; \
	else \
		echo "$(GREEN)Testing services/$(SERVICE)...$(RESET)"; \
		cd services/$(SERVICE) && pytest tests/ -v; \
	fi

test-integration: ## Run integration tests only
	@echo "$(GREEN)Running integration tests...$(RESET)"
	@for service in services/*; do \
		if [ -d "$$service/tests/integration" ]; then \
			echo "$(BLUE)Integration tests for $$service...$(RESET)"; \
			cd $$service && pytest tests/integration/ -v && cd ../..; \
		fi \
	done

test-unit: ## Run unit tests only
	@echo "$(GREEN)Running unit tests...$(RESET)"
	@for service in services/*; do \
		if [ -d "$$service/tests/unit" ]; then \
			echo "$(BLUE)Unit tests for $$service...$(RESET)"; \
			cd $$service && pytest tests/unit/ -v && cd ../..; \
		fi \
	done

# ════════════════════════════════════════════════════════════════════════════════
# CODE QUALITY
# ════════════════════════════════════════════════════════════════════════════════
lint: ## Run all linters (ruff, mypy, bandit)
	@echo "$(GREEN)Running linters...$(RESET)"
	@$(MAKE) lint-ruff
	@$(MAKE) lint-mypy
	@$(MAKE) lint-bandit
	@echo "$(GREEN)✓ All linters passed$(RESET)"

lint-ruff: ## Run Ruff linter
	@echo "$(BLUE)Running Ruff...$(RESET)"
	@ruff check services/ shared/ || (echo "$(RED)✗ Ruff failed$(RESET)" && exit 1)

lint-mypy: ## Run Mypy type checker
	@echo "$(BLUE)Running Mypy...$(RESET)"
	@mypy --config-file pyproject.toml services/ shared/ || (echo "$(RED)✗ Mypy failed$(RESET)" && exit 1)

lint-bandit: ## Run Bandit security checker
	@echo "$(BLUE)Running Bandit...$(RESET)"
	@bandit -r services/ shared/ -ll || (echo "$(RED)✗ Bandit failed$(RESET)" && exit 1)

format: ## Format code with ruff
	@echo "$(GREEN)Formatting code...$(RESET)"
	@ruff format services/ shared/
	@echo "$(GREEN)✓ Code formatted$(RESET)"

format-check: ## Check if code needs formatting
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	@ruff format --check services/ shared/

# ════════════════════════════════════════════════════════════════════════════════
# DATABASE OPERATIONS
# ════════════════════════════════════════════════════════════════════════════════
db-migrate: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) exec db_postgres_service alembic upgrade head
	@echo "$(GREEN)✓ Migrations applied$(RESET)"

db-rollback: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) exec db_postgres_service alembic downgrade -1
	@echo "$(GREEN)✓ Rollback complete$(RESET)"

db-migration: ## Create new migration (make db-migration MSG="add users table")
	@if [ -z "$(MSG)" ]; then \
		echo "$(RED)Error: MSG not specified. Usage: make db-migration MSG='add users table'$(RESET)"; \
	else \
		echo "$(GREEN)Creating migration: $(MSG)$(RESET)"; \
		docker-compose -f $(COMPOSE_FILE) exec db_postgres_service alembic revision --autogenerate -m "$(MSG)"; \
	fi

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)⚠  WARNING: This will destroy all data!$(RESET)"
	@echo "$(YELLOW)Press Ctrl+C to cancel, or Enter to continue...$(RESET)"
	@read confirm
	@echo "$(YELLOW)Resetting database...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) down -v
	docker-compose -f $(COMPOSE_FILE) up -d postgres mongodb
	@sleep 5
	@$(MAKE) db-migrate
	@echo "$(GREEN)✓ Database reset complete$(RESET)"

db-shell-postgres: ## Open PostgreSQL shell
	@docker-compose -f $(COMPOSE_FILE) exec postgres psql -U postgres -d $${POSTGRES_DB}

db-shell-mongo: ## Open MongoDB shell
	@docker-compose -f $(COMPOSE_FILE) exec mongodb mongosh $${MONGO_DATABASE}

# ════════════════════════════════════════════════════════════════════════════════
# MONITORING & OBSERVABILITY
# ════════════════════════════════════════════════════════════════════════════════
monitoring-up: ## Start monitoring stack (Prometheus, Grafana, Jaeger)
	@echo "$(GREEN)Starting monitoring stack...$(RESET)"
	docker-compose --profile observability -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✓ Monitoring stack started$(RESET)"
	@echo "$(BLUE)Grafana:    http://localhost:3000 (admin/admin)$(RESET)"
	@echo "$(BLUE)Prometheus: http://localhost:9090$(RESET)"
	@echo "$(BLUE)Jaeger:     http://localhost:16686$(RESET)"

monitoring-down: ## Stop monitoring stack
	@echo "$(YELLOW)Stopping monitoring stack...$(RESET)"
	docker-compose --profile observability -f $(COMPOSE_FILE) down

# ════════════════════════════════════════════════════════════════════════════════
# CLEANUP
# ════════════════════════════════════════════════════════════════════════════════
clean: ## Clean up temporary files and caches
	@echo "$(YELLOW)Cleaning temporary files...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(RESET)"

clean-docker: ## Remove all Docker containers, images, and volumes
	@echo "$(RED)⚠  WARNING: This will remove all Docker resources!$(RESET)"
	@echo "$(YELLOW)Press Ctrl+C to cancel, or Enter to continue...$(RESET)"
	@read confirm
	@echo "$(YELLOW)Cleaning Docker resources...$(RESET)"
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all --remove-orphans
	@echo "$(GREEN)✓ Docker cleanup complete$(RESET)"

prune: ## Prune Docker system (removes unused images and volumes)
	@echo "$(YELLOW)Pruning Docker system...$(RESET)"
	docker system prune -af
	docker volume prune -f
	@echo "$(GREEN)✓ Docker system pruned$(RESET)"

# ════════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ════════════════════════════════════════════════════════════════════════════════
health: ## Check health of all services
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(GREEN)Service Health Check:$(RESET)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@curl -s http://localhost:8000/api/v1/health | jq . && echo "$(GREEN)✓ API Service$(RESET)" || echo "$(RED)✗ API Service$(RESET)"
	@curl -s http://localhost:8001/health | jq . && echo "$(GREEN)✓ PostgreSQL Service$(RESET)" || echo "$(RED)✗ PostgreSQL Service$(RESET)"
	@curl -s http://localhost:8002/health | jq . && echo "$(GREEN)✓ MongoDB Service$(RESET)" || echo "$(RED)✗ MongoDB Service$(RESET)"

backup: ## Backup databases
	@echo "$(GREEN)Creating database backups...$(RESET)"
	@mkdir -p backups
	@docker-compose -f $(COMPOSE_FILE) exec -T postgres pg_dump -U postgres $${POSTGRES_DB} > backups/postgres_$$(date +%Y%m%d_%H%M%S).sql
	@docker-compose -f $(COMPOSE_FILE) exec -T mongodb mongodump --archive > backups/mongodb_$$(date +%Y%m%d_%H%M%S).archive
	@echo "$(GREEN)✓ Backups created in ./backups/$(RESET)"

restore-postgres: ## Restore PostgreSQL backup (make restore-postgres FILE=backups/postgres_20231201.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: FILE not specified. Usage: make restore-postgres FILE=backups/postgres_20231201.sql$(RESET)"; \
	else \
		echo "$(YELLOW)Restoring PostgreSQL from $(FILE)...$(RESET)"; \
		docker-compose -f $(COMPOSE_FILE) exec -T postgres psql -U postgres $${POSTGRES_DB} < $(FILE); \
		echo "$(GREEN)✓ PostgreSQL restored$(RESET)"; \
	fi

env: ## Show current environment variables
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(GREEN)Environment Variables:$(RESET)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@cat .env | grep -v '^#' | grep -v '^$$'

version: ## Show versions of all components
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(GREEN)Component Versions:$(RESET)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(RESET)"
	@echo "Python:     $$(python --version)"
	@echo "Docker:     $$(docker --version)"
	@echo "Compose:    $$(docker-compose --version)"
	@echo "PostgreSQL: $$(docker-compose -f $(COMPOSE_FILE) exec -T postgres psql --version)"
	@echo "MongoDB:    $$(docker-compose -f $(COMPOSE_FILE) exec -T mongodb mongosh --version | head -1)"
	@echo "Redis:      $$(docker-compose -f $(COMPOSE_FILE) exec -T redis redis-server --version)"
