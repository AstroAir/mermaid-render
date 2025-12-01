# Contributing to DiagramAid

Thank you for your interest in contributing to DiagramAid! We welcome contributions from the community and are grateful for your help in making this project better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [contact@diagramaid.dev](mailto:contact@diagramaid.dev).

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- UV package manager (recommended) or pip

### Setting up the development environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/diagramaid.git
cd diagramaid

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev,cache,interactive,ai,docs]"

# Or using UV (recommended)
uv sync --all-extras
```

### Verify installation

```bash
# Run the demo to verify everything works
python demo.py

# Run tests
pytest

# Check code style
black --check diagramaid tests
ruff check diagramaid tests
mypy diagramaid
```

## Making Changes

### Branch naming

Use descriptive branch names:

- `feature/add-new-diagram-type`
- `fix/validation-error-handling`
- `docs/improve-api-documentation`
- `refactor/optimize-rendering-performance`

### Commit messages

Follow conventional commit format:

- `feat: add support for timeline diagrams`
- `fix: resolve validation error for complex flowcharts`
- `docs: update API documentation for themes`
- `test: add integration tests for PDF rendering`
- `refactor: optimize diagram parsing performance`

## Testing

We maintain high test coverage and require tests for all new features.

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=diagramaid --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests

# Run tests for specific modules
pytest tests/unit/test_models.py
pytest tests/integration/test_end_to_end.py
```

### Writing tests

- Write unit tests for all new functions and classes
- Add integration tests for new features
- Include edge cases and error conditions
- Use descriptive test names
- Follow the existing test structure

Example test:

```python
def test_flowchart_node_creation():
    """Test that flowchart nodes are created correctly."""
    flowchart = FlowchartDiagram()
    flowchart.add_node("A", "Start", shape="circle")

    assert len(flowchart.nodes) == 1
    assert flowchart.nodes[0].id == "A"
    assert flowchart.nodes[0].label == "Start"
    assert flowchart.nodes[0].shape == "circle"
```

## Code Style

We use several tools to maintain code quality:

### Formatting

- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **MyPy**: Type checking

### Running code quality checks

```bash
# Format code
black diagramaid tests

# Check formatting
black --check diagramaid tests

# Lint code
ruff check diagramaid tests

# Fix linting issues
ruff check --fix diagramaid tests

# Type checking
mypy diagramaid
```

### Code style guidelines

- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Follow PEP 8 style guidelines
- Keep functions focused and small
- Use descriptive variable and function names
- Add comments for complex logic

## Submitting Changes

### Pull Request Process

1. **Update documentation**: Ensure any new features are documented
2. **Add tests**: Include tests for new functionality
3. **Update changelog**: Add entry to CHANGELOG.md
4. **Check CI**: Ensure all CI checks pass
5. **Request review**: Ask for review from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changelog updated
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Minimal steps to reproduce the problem
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: Python version, OS, package version
- **Code sample**: Minimal code that reproduces the issue

### Security Issues

For security vulnerabilities, please email [security@diagramaid.dev](mailto:security@diagramaid.dev) instead of creating a public issue.

## Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists or is planned
2. Describe the use case and motivation
3. Provide examples of how the feature would be used
4. Consider implementation complexity and maintenance burden

## Development Guidelines

### Adding New Diagram Types

1. Create model class in `diagramaid/models/`
2. Add validation logic
3. Include comprehensive tests
4. Update documentation and examples
5. Add to main `__init__.py` exports

### Adding New Renderers

1. Create renderer class in `diagramaid/renderers/`
2. Implement required interface methods
3. Add error handling and validation
4. Include unit and integration tests
5. Update configuration options

### Performance Considerations

- Profile performance-critical code
- Use caching where appropriate
- Minimize external dependencies
- Consider memory usage for large diagrams
- Add performance tests for critical paths

## Questions?

If you have questions about contributing, please:

1. Check the documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Email [contact@diagramaid.dev](mailto:contact@diagramaid.dev)

Thank you for contributing to DiagramAid! 🎉
