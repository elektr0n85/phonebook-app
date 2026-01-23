# Phonebook Application Makefile
# Convenient commands for development and deployment

.PHONY: help install dev test clean deploy

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Phonebook Application - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==============================================================================
# Development
# ==============================================================================

install: ## Install all dependencies (backend + frontend)
	@echo "Installing backend dependencies..."
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Installation complete!"

dev-backend: ## Start backend development server
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

dev: ## Start both backend and frontend (requires tmux)
	tmux new-session -d -s phonebook 'make dev-backend'
	tmux split-window -h 'make dev-frontend'
	tmux attach-session -t phonebook

# ==============================================================================
# Testing
# ==============================================================================

test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && . venv/bin/activate && pytest
	@echo "✅ All tests passed!"

test-backend: ## Run backend tests with coverage
	cd backend && . venv/bin/activate && pytest --cov=app --cov-report=html --cov-report=term

test-security: ## Run security tests only
	cd backend && . venv/bin/activate && pytest -m security -v

test-unit: ## Run unit tests only
	cd backend && . venv/bin/activate && pytest -m unit -v

test-integration: ## Run integration tests only
	cd backend && . venv/bin/activate && pytest -m integration -v

coverage: ## Generate coverage report
	cd backend && . venv/bin/activate && pytest --cov=app --cov-report=html
	@echo "Coverage report: backend/htmlcov/index.html"

# ==============================================================================
# Code Quality
# ==============================================================================

lint: ## Run linters (backend)
	cd backend && . venv/bin/activate && pylint app/
	cd frontend && npm run lint

format: ## Format code (black + prettier)
	cd backend && . venv/bin/activate && black app/ tests/
	cd frontend && npm run format

security-scan: ## Run security scans
	@echo "Running Bandit (security linter)..."
	cd backend && . venv/bin/activate && bandit -r app/
	@echo "Running Safety (dependency check)..."
	cd backend && . venv/bin/activate && safety check
	@echo "Running npm audit..."
	cd frontend && npm audit

type-check: ## Run type checking
	cd backend && . venv/bin/activate && mypy app/

# ==============================================================================
# Database
# ==============================================================================

db-init: ## Initialize database
	cd backend && . venv/bin/activate && python init_db.py

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d db; \
		sleep 5; \
		make db-init; \
	fi

db-backup: ## Backup database
	docker-compose exec -T db pg_dump -U phonebook_user phonebook_db | gzip > backup_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "✅ Backup created!"

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U phonebook_user phonebook_db

# ==============================================================================
# Docker
# ==============================================================================

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start all services with Docker
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## View logs (all services)
	docker-compose logs -f

docker-logs-backend: ## View backend logs
	docker-compose logs -f backend

docker-logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

docker-restart: ## Restart all services
	docker-compose restart

docker-ps: ## Show running containers
	docker-compose ps

docker-clean: ## Remove all containers, volumes, images
	docker-compose down -v --rmi all
	docker system prune -af

# ==============================================================================
# Deployment
# ==============================================================================

deploy-check: ## Run pre-deployment checks
	@echo "Running pre-deployment checks..."
	@make test
	@make security-scan
	@echo "Checking environment variables..."
	@test -f .env || (echo "❌ .env file not found!" && exit 1)
	@grep -q "CHANGE_ME" .env && (echo "❌ Default secrets found in .env!" && exit 1) || true
	@echo "✅ All checks passed!"

deploy-prod: ## Deploy to production (Docker)
	@echo "Deploying to production..."
	@make deploy-check
	git pull
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✅ Deployment complete!"

deploy-rollback: ## Rollback to previous version
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
	git checkout HEAD~1
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✅ Rolled back to previous version"

# ==============================================================================
# Utilities
# ==============================================================================

clean: ## Clean temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	@echo "✅ Cleaned temporary files!"

generate-secret: ## Generate secret key
	@python3 -c "import secrets; print(secrets.token_hex(32))"

health-check: ## Check application health
	@curl -f http://localhost:8000/health || echo "❌ Backend is down!"
	@curl -f http://localhost/health || echo "❌ Frontend is down!"

env-setup: ## Setup environment file from example
	@test -f .env && echo "⚠️  .env already exists!" || cp .env.example .env
	@echo "📝 Edit .env file with your configuration"

# ==============================================================================
# Documentation
# ==============================================================================

docs: ## Open documentation
	@echo "Opening documentation..."
	@open README.md || xdg-open README.md || echo "README.md"

docs-api: ## Open API documentation
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "http://localhost:8000/docs"

# ==============================================================================
# Production Commands
# ==============================================================================

prod-logs: ## View production logs
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

prod-restart: ## Restart production services
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart

prod-status: ## Check production status
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
	@make health-check

# ==============================================================================
# CI/CD
# ==============================================================================

ci: ## Run CI checks (tests, lint, security)
	@make test
	@make lint
	@make security-scan
	@echo "✅ CI checks passed!"

# ==============================================================================
# Quick Commands
# ==============================================================================

start: docker-up ## Quick start (alias for docker-up)

stop: docker-down ## Quick stop (alias for docker-down)

restart: docker-restart ## Quick restart (alias for docker-restart)

logs: docker-logs ## Quick logs (alias for docker-logs)
