# Development Guide

This document provides a comprehensive guide for developers working on Mermaid Render.

## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Quick Start

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git
- Make (optional, for convenience)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/mermaid-render.git
cd mermaid-render

# Install with development dependencies using uv
uv sync --extra dev --extra cache --extra interactive --extra ai --extra collaboration --extra docs

# Or using pip
pip install -e ".[dev,cache,interactive,ai,collaboration,docs]"

# Install pre-commit hooks
pre-commit install

# Verify installation
make test
```

## Project Structure

```text
mermaid-render/
├── .github/                    # GitHub configurations
│   ├── workflows/             # CI/CD workflows
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── pull_request_template.md
├── docs/                      # Documentation
├── examples/                  # Usage examples
├── mermaid_render/           # Main package
│   ├── ai/                   # AI-powered features

│   ├── diagrams/            # Diagram implementations
│   ├── renderers/           # Output renderers
│   ├── templates/           # Template system
│   ├── themes/              # Theme management
│   └── validation/          # Input validation
├── tests/                   # Test suite
├── pyproject.toml          # Project configuration
├── requirements.txt        # Core dependencies
├── requirements-dev.txt    # Development dependencies
├── uv.lock                # Locked dependencies
└── tox.ini                # Testing environments
```

## Development Workflow

### Making Changes

1. **Create a branch** for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines.

3. **Run tests** to ensure nothing is broken:

   ```bash
   make test
   ```

4. **Run code quality checks**:

   ```bash
   make check-all
   ```

5. **Commit your changes** with a descriptive message:

   ```bash
   git commit -m "feat: add new diagram type support"
   ```

6. **Push your branch** and create a pull request.

### Using Make Commands

The project includes a comprehensive Makefile for common development tasks:

```bash
# Setup
make install           # Install package in development mode
make install-dev       # Install with all development dependencies
make setup-dev         # Complete development environment setup

# Testing
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-coverage     # Run tests with coverage report

# Code Quality
make lint              # Run linting checks
make format            # Format code with black and ruff
make type-check        # Run type checking with mypy
make check-all         # Run all code quality checks

# Documentation
make docs              # Build documentation
make docs-serve        # Serve documentation locally

# Build & Release
make build             # Build package for distribution
make clean             # Clean build artifacts
```

## Code Quality

### Code Style

- **Formatting**: We use [Black](https://black.readthedocs.io/) with 88-character line length
- **Linting**: We use [Ruff](https://beta.ruff.rs/) for fast Python linting
- **Type Checking**: We use [MyPy](http://mypy-lang.org/) for static type checking
- **Import Sorting**: Handled automatically by Ruff

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit to ensure code quality:

- Trailing whitespace removal
- End-of-file fixer
- YAML/TOML/JSON validation
- Python syntax validation
- Code formatting with Black
- Linting with Ruff
- Type checking with MyPy

### Running Quality Checks

```bash
# Run all checks
make check-all

# Run individual checks
make lint          # Linting only
make format        # Format code
make type-check    # Type checking only

# Fix formatting issues
make format
```

## Testing

### Test Structure

Tests are organized by type and functionality:

```text
tests/
├── unit/                  # Unit tests
├── integration/           # Integration tests
├── browser/              # Browser compatibility tests
└── fixtures/             # Test fixtures and data
```

### Test Categories

Tests are marked with pytest markers for selective running:

- `unit`: Fast unit tests
- `integration`: Integration tests
- `slow`: Tests that take longer to run
- `network`: Tests requiring network access
- `svg`: SVG rendering tests
- `browser`: Browser compatibility tests

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m "not slow"             # Exclude slow tests
pytest -m "integration and svg"  # Integration tests for SVG

# Run with coverage
make test-coverage

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- Write unit tests for all new functionality
- Include integration tests for complete workflows
- Use descriptive test names that explain what is being tested
- Follow the AAA pattern: Arrange, Act, Assert
- Mock external dependencies in unit tests

## Documentation

### Building Documentation

```bash
# Build documentation
make docs

# Serve documentation locally
make docs-serve
```

### Documentation Guidelines

- All public APIs must have docstrings
- Use Google-style docstrings
- Include type hints in function signatures
- Provide usage examples in docstrings
- Update README.md for user-facing changes

## Release Process

### Version Management

- We follow [Semantic Versioning](https://semver.org/)
- Version is managed in `pyproject.toml`
- Update `CHANGELOG.md` for all releases

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update** `CHANGELOG.md` with release notes
3. **Create and push** a version tag:

   ```bash
   git tag v1.x.x
   git push origin v1.x.x
   ```

4. **GitHub Actions** will automatically build and publish to PyPI

### Testing Releases

Before releasing:

```bash
# Run full test suite
make test

# Test package building
make build

# Test installation in clean environment
make clean
pip install dist/*.whl
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you've installed the package in development mode (`pip install -e .`)
2. **Pre-commit failures**: Run `make format` to fix formatting issues
3. **Test failures**: Check that all dependencies are installed with `make install-dev`
4. **Type check errors**: Ensure all type hints are correct and imports are available

### Getting Help

- Check existing [GitHub Issues](https://github.com/mermaid-render/mermaid-render/issues)
- Review the [Contributing Guidelines](CONTRIBUTING.md)
- Join our discussions in GitHub Discussions
- Contact maintainers at [maintainers@mermaid-render.dev](mailto:maintainers@mermaid-render.dev)
