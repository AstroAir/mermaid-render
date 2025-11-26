# Makefile for Mermaid Render development

.PHONY: help install install-dev test test-unit test-integration test-coverage lint format type-check clean build docs demo setup-dev

# Default target
help:
	@echo "Mermaid Render Development Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup:"
	@echo "  install       Install package in development mode"
	@echo "  install-dev   Install with all development dependencies"
	@echo "  setup-dev     Complete development environment setup (enhanced)"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests with coverage (enhanced)"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  test-fast     Run tests excluding slow ones"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          Run linting checks (enhanced)"
	@echo "  format        Format code with black and ruff (enhanced)"
	@echo "  type-check    Run type checking with mypy (enhanced)"
	@echo "  check-all     Run all code quality checks (enhanced)"
	@echo "  qa-check      Comprehensive quality assurance"
	@echo "  security      Run security checks (enhanced)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs          Build documentation (enhanced)"
	@echo "  docs-serve    Serve documentation locally"
	@echo "  demo          Run the demo script"
	@echo ""
	@echo "Build & Release:"
	@echo "  build         Build package for distribution (enhanced)"
	@echo "  clean         Clean build artifacts (enhanced)"
	@echo "  release       Build and upload to PyPI (requires auth)"
	@echo ""
	@echo "Performance & Benchmarking:"
	@echo "  benchmark     Run performance benchmarks (new)"
	@echo "  benchmark-compare  Compare with previous benchmark results"
	@echo ""
	@echo "Docker Operations:"
	@echo "  docker-build  Build Docker images"
	@echo "  docker-run    Run development container"
	@echo "  docker-test   Run tests in container"
	@echo "  docker-clean  Clean Docker resources"
	@echo "  docker-deploy Deploy Docker image"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy-staging     Deploy to staging environment"
	@echo "  deploy-production  Deploy to production environment"
	@echo "  deploy-dry-run     Dry run deployment to staging"
	@echo ""
	@echo "Database Management:"
	@echo "  db-init       Initialize database migration system"
	@echo "  db-migrate    Apply pending database migrations"
	@echo "  db-status     Show migration status"
	@echo "  db-rollback   Rollback last migration"
	@echo "  db-seed       Seed database with test data"
	@echo ""
	@echo "Utilities:"
	@echo "  deps-update   Update dependencies"
	@echo "  env-info      Show environment information"
	@echo "  check-tools   Verify required tools are available"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,cache,interactive,ai,docs]"

setup-dev:
	@echo "Setting up development environment with enhanced script..."
	python scripts/setup-dev.py --verbose

# Testing targets
test:
	python scripts/dev.py test

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-coverage:
	python scripts/dev.py test

test-fast:
	pytest -m "not slow"

test-verbose:
	pytest -v

# Category-specific tests
test-svg:
	pytest tests/e2e/test_svg_rendering.py

test-browser:
	pytest tests/e2e/test_browser_compatibility.py

test-error-handling:
	pytest tests/unit/test_error_handling.py

test-theme:
	pytest tests/e2e/test_theme_support.py

test-export:
	pytest tests/e2e/test_export_workflows.py

test-remote:
	pytest tests/e2e/test_remote_rendering.py

test-performance:
	pytest tests/performance/

test-regression:
	pytest tests/regression/

test-e2e:
	pytest tests/e2e/

# AI module tests
test-ai:
	pytest tests/unit/ai/

# Cache module tests
test-cache:
	pytest tests/unit/cache/

# Model tests
test-models:
	pytest tests/unit/models/

# Renderer tests
test-renderers:
	pytest tests/unit/renderers/

# Code quality targets
lint:
	python scripts/dev.py lint

format:
	python scripts/dev.py format

type-check:
	python scripts/dev.py type-check

check-all:
	python scripts/dev.py all

qa-check:
	python scripts/qa-check.py

security:
	python scripts/dev.py security

# Documentation targets
docs:
	python scripts/dev.py docs

docs-serve:
	@echo "Serving documentation locally..."
	@if [ -d "docs/_build/html" ]; then \
		cd docs/_build/html && python -m http.server 8000; \
	else \
		echo "Documentation not built. Run 'make docs' first."; \
	fi

demo:
	@echo "Running demo script..."
	python demo.py

# Build and release targets
clean:
	python scripts/dev.py clean

build:
	python scripts/dev.py build

release: build
	@echo "Uploading to PyPI..."
	@echo "Make sure you have configured your PyPI credentials!"
	twine upload dist/*

# Utility targets
benchmark:
	python scripts/benchmark.py

benchmark-compare:
	python scripts/benchmark.py --compare benchmark_results_*.json

deps-update:
	@echo "Updating dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		uv lock --upgrade; \
	else \
		pip list --outdated; \
	fi

# Development workflow targets
pre-commit: format lint type-check test-fast
	@echo "Pre-commit checks completed successfully!"

ci: check-all test-coverage
	@echo "CI checks completed successfully!"

# Quick development targets
dev-test: format test-fast
	@echo "Quick development test cycle completed!"

dev-check: format lint
	@echo "Quick development check completed!"

# Environment info
env-info:
	@echo "Environment Information:"
	@echo "======================="
	@python --version
	@pip --version
	@echo "Installed packages:"
	@pip list | grep -E "(mermaid|pytest|black|ruff|mypy)"

# Setup documentation (if not exists)
setup-docs:
	@echo "Setting up documentation structure..."
	@mkdir -p docs
	@if [ ! -f "docs/conf.py" ]; then \
		echo "Creating basic Sphinx configuration..."; \
		cd docs && sphinx-quickstart -q -p "Mermaid Render" -a "Mermaid Render Team" -v "1.0.0" --ext-autodoc --ext-viewcode --makefile --no-batchfile .; \
	fi

# Docker targets
docker-build:
	python scripts/docker-manager.py build

docker-run:
	python scripts/docker-manager.py run

docker-test:
	python scripts/docker-manager.py test

docker-clean:
	python scripts/docker-manager.py clean

docker-deploy:
	python scripts/docker-manager.py deploy

# Deployment targets
deploy-staging:
	python scripts/deploy.py staging

deploy-production:
	python scripts/deploy.py production

deploy-dry-run:
	python scripts/deploy.py staging --dry-run

# Database targets
db-init:
	python scripts/db-migrate.py init

db-migrate:
	python scripts/db-migrate.py migrate

db-status:
	python scripts/db-migrate.py status

db-rollback:
	python scripts/db-migrate.py rollback

db-seed:
	python scripts/db-migrate.py seed

# Performance profiling
profile:
	@echo "Running performance profiling..."
	@python -m cProfile -o profile.stats demo.py
	@python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

# Git hooks
install-hooks:
	@echo "Installing git hooks..."
	@echo "#!/bin/sh\nmake pre-commit" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Git hooks installed!"

# Version management
version:
	@python -c "import mermaid_render; print(f'Version: {mermaid_render.__version__}')"

# Check if all required tools are available
check-tools:
	@echo "Checking required tools..."
	@command -v python >/dev/null 2>&1 || { echo "Python not found!"; exit 1; }
	@command -v pip >/dev/null 2>&1 || { echo "Pip not found!"; exit 1; }
	@python -c "import pytest" 2>/dev/null || { echo "Pytest not installed!"; exit 1; }
	@python -c "import black" 2>/dev/null || { echo "Black not installed!"; exit 1; }
	@python -c "import ruff" 2>/dev/null || { echo "Ruff not installed!"; exit 1; }
	@python -c "import mypy" 2>/dev/null || { echo "MyPy not installed!"; exit 1; }
	@echo "All required tools are available!"
