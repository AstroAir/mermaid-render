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
	@echo "  setup-dev     Complete development environment setup"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  test-fast     Run tests excluding slow ones"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black and ruff"
	@echo "  type-check    Run type checking with mypy"
	@echo "  check-all     Run all code quality checks"
	@echo ""
	@echo "Documentation:"
	@echo "  docs          Build documentation"
	@echo "  docs-serve    Serve documentation locally"
	@echo "  demo          Run the demo script"
	@echo ""
	@echo "Build & Release:"
	@echo "  build         Build package for distribution"
	@echo "  clean         Clean build artifacts"
	@echo "  release       Build and upload to PyPI (requires auth)"
	@echo ""
	@echo "Utilities:"
	@echo "  benchmark     Run performance benchmarks"
	@echo "  security      Run security checks"
	@echo "  deps-update   Update dependencies"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,cache,interactive,ai,docs]"

setup-dev: install-dev
	@echo "Setting up development environment..."
	@echo "Installing pre-commit hooks..."
	@pip install pre-commit
	@pre-commit install
	@echo "Development environment ready!"

# Testing targets
test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-coverage:
	pytest --cov=mermaid_render --cov-report=html --cov-report=term

test-fast:
	pytest -m "not slow"

test-verbose:
	pytest -v

# Category-specific tests
test-svg:
	pytest tests/svg

test-browser:
	pytest tests/browser_compatibility

test-error-handling:
	pytest tests/error_handling

test-theme:
	pytest tests/theme

test-export:
	pytest tests/export

test-remote:
	pytest tests/remote

test-performance:
	pytest tests/performance

# Code quality targets
lint:
	@echo "Running ruff..."
	ruff check mermaid_render tests
	@echo "Checking import sorting..."
	ruff check --select I mermaid_render tests

format:
	@echo "Formatting with black..."
	black mermaid_render tests examples
	@echo "Fixing imports with ruff..."
	ruff check --fix --select I mermaid_render tests examples

type-check:
	@echo "Running mypy..."
	mypy mermaid_render

check-all: lint type-check
	@echo "Running black check..."
	black --check mermaid_render tests examples
	@echo "All code quality checks passed!"

# Documentation targets
docs:
	@echo "Building documentation..."
	@if [ -d "docs" ]; then \
		cd docs && make html; \
	else \
		echo "Documentation directory not found. Run 'make setup-docs' first."; \
	fi

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
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	@echo "Building package..."
	python -m build

release: build
	@echo "Uploading to PyPI..."
	@echo "Make sure you have configured your PyPI credentials!"
	twine upload dist/*

# Utility targets
benchmark:
	@echo "Running performance benchmarks..."
	@if [ -f "benchmarks/run_benchmarks.py" ]; then \
		python benchmarks/run_benchmarks.py; \
	else \
		echo "Benchmark script not found."; \
	fi

security:
	@echo "Running security checks..."
	@pip install safety bandit
	safety check
	bandit -r mermaid_render/

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

# Docker targets (if Docker is available)
docker-build:
	@if command -v docker >/dev/null 2>&1; then \
		docker build -t mermaid-render .; \
	else \
		echo "Docker not available"; \
	fi

docker-test:
	@if command -v docker >/dev/null 2>&1; then \
		docker run --rm mermaid-render make test; \
	else \
		echo "Docker not available"; \
	fi

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
