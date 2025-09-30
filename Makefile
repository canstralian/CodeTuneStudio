.PHONY: help install install-dev test lint format clean run db-upgrade db-migrate pre-commit build docs

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)CodeTuneStudio - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "$(GREEN)Usage:$(NC)\n  make $(YELLOW)<target>$(NC)\n\n$(GREEN)Targets:$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	@command -v uv >/dev/null 2>&1 || (echo "$(YELLOW)Installing uv...$(NC)" && curl -LsSf https://astral.sh/uv/install.sh | sh)
	uv pip install -e .
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@command -v uv >/dev/null 2>&1 || (echo "$(YELLOW)Installing uv...$(NC)" && curl -LsSf https://astral.sh/uv/install.sh | sh)
	uv pip install -e ".[dev]"
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

pre-commit-setup: ## Setup pre-commit hooks
	@echo "$(BLUE)Setting up pre-commit hooks...$(NC)"
	pip install pre-commit
	pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

env-setup: ## Setup environment from template
	@echo "$(BLUE)Setting up environment...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env from template$(NC)"; \
		echo "$(YELLOW)⚠ Please edit .env with your configuration$(NC)"; \
	else \
		echo "$(YELLOW)⚠ .env already exists, skipping$(NC)"; \
	fi

test: ## Run all tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v
	@echo "$(GREEN)✓ Tests completed$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term --cov-report=xml
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"
	@echo "$(YELLOW)Open htmlcov/index.html to view detailed report$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/ -v -m unit
	@echo "$(GREEN)✓ Unit tests completed$(NC)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/ -v -m integration
	@echo "$(GREEN)✓ Integration tests completed$(NC)"

lint: ## Lint code with Ruff
	@echo "$(BLUE)Linting code...$(NC)"
	ruff check .
	@echo "$(GREEN)✓ Linting completed$(NC)"

lint-fix: ## Lint and auto-fix issues
	@echo "$(BLUE)Linting and fixing code...$(NC)"
	ruff check --fix .
	@echo "$(GREEN)✓ Auto-fixes applied$(NC)"

format: ## Format code with Ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	ruff format .
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check if code is formatted
	@echo "$(BLUE)Checking code formatting...$(NC)"
	ruff format --check .

typecheck: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	pip install mypy types-requests
	mypy . --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking completed$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

run: ## Run the Streamlit application
	@echo "$(BLUE)Starting CodeTuneStudio...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)✗ .env file not found. Run 'make env-setup' first$(NC)"; \
		exit 1; \
	fi
	python app.py

db-init: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	python manage.py db init
	@echo "$(GREEN)✓ Database initialized$(NC)"

db-migrate: ## Create database migration
	@echo "$(BLUE)Creating database migration...$(NC)"
	@read -p "Migration message: " msg; \
	python manage.py db migrate -m "$$msg"
	@echo "$(GREEN)✓ Migration created$(NC)"

db-upgrade: ## Apply database migrations
	@echo "$(BLUE)Applying database migrations...$(NC)"
	python manage.py db upgrade
	@echo "$(GREEN)✓ Migrations applied$(NC)"

db-downgrade: ## Rollback last migration
	@echo "$(BLUE)Rolling back last migration...$(NC)"
	python manage.py db downgrade
	@echo "$(GREEN)✓ Migration rolled back$(NC)"

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)⚠ WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -f database.db fallback.db; \
		echo "$(YELLOW)Database files deleted$(NC)"; \
		make db-upgrade; \
	else \
		echo "$(YELLOW)Operation cancelled$(NC)"; \
	fi

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	pip install build
	python -m build
	@echo "$(GREEN)✓ Build completed: dist/$(NC)"

build-check: ## Check distribution packages
	@echo "$(BLUE)Checking distribution...$(NC)"
	pip install twine
	twine check dist/*
	@echo "$(GREEN)✓ Distribution check passed$(NC)"

publish-test: build build-check ## Publish to Test PyPI
	@echo "$(BLUE)Publishing to Test PyPI...$(NC)"
	@echo "$(YELLOW)Enter your Test PyPI credentials$(NC)"
	twine upload --repository testpypi dist/*
	@echo "$(GREEN)✓ Published to Test PyPI$(NC)"

publish: build build-check ## Publish to PyPI (requires credentials)
	@echo "$(RED)⚠ Publishing to PyPI!$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		twine upload dist/*; \
		echo "$(GREEN)✓ Published to PyPI$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled$(NC)"; \
	fi

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t codetunestudio:latest .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -p 7860:7860 --env-file .env codetunestudio:latest

logs: ## View application logs
	@echo "$(BLUE)Viewing logs...$(NC)"
	tail -f codetunestudio.log

pre-commit-run: ## Run pre-commit on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit checks completed$(NC)"

security-check: ## Run security checks with Bandit
	@echo "$(BLUE)Running security checks...$(NC)"
	bandit -r . -f txt
	bandit -r . -f json -o bandit-report.json
	@echo "$(GREEN)✓ Security scan completed$(NC)"
	@echo "$(YELLOW)Detailed report saved to bandit-report.json$(NC)"

security-full: ## Run comprehensive security checks
	@echo "$(BLUE)Running comprehensive security checks...$(NC)"
	pip install bandit safety
	bandit -r . -c pyproject.toml
	safety check
	@echo "$(GREEN)✓ All security checks completed$(NC)"

deps-update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	uv pip compile pyproject.toml --upgrade -o requirements.txt
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

deps-tree: ## Show dependency tree
	@echo "$(BLUE)Dependency tree:$(NC)"
	pip install pipdeptree
	pipdeptree

setup: install-dev env-setup pre-commit-setup db-upgrade ## Complete development setup
	@echo ""
	@echo "$(GREEN)✓✓✓ Development environment ready! ✓✓✓$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Edit .env with your configuration"
	@echo "  2. Run '$(YELLOW)make run$(NC)' to start the application"
	@echo "  3. Visit http://localhost:7860"
	@echo ""

ci: lint test ## Run CI checks locally
	@echo "$(GREEN)✓ CI checks passed$(NC)"

release-check: lint test format-check ## Check if ready for release
	@echo "$(BLUE)Checking release readiness...$(NC)"
	@echo "$(GREEN)✓ All checks passed - ready for release!$(NC)"

.PHONY: help install install-dev test lint format clean run db-upgrade
