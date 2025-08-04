# Mermaid Render Test Suite

This directory contains all the tests for the Mermaid Render library. The tests are organized into logical categories to make it easier to maintain and run specific test groups.

## Test Organization

- **unit/**: Unit tests for individual components
- **integration/**: Integration tests that test multiple components working together
- **performance/**: Performance and benchmark tests
- **svg/**: Tests for SVG rendering functionality
- **browser_compatibility/**: Tests for browser compatibility
- **error_handling/**: Tests for error handling scenarios
- **theme/**: Tests for theme support features
- **export/**: Tests for export functionality
- **remote/**: Tests for remote rendering capabilities
- **fixtures/**: Shared test fixtures and sample data

## Running Tests

You can use the provided Makefile targets to run specific test groups:

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run SVG rendering tests
make test-svg

# Run with coverage report
make test-coverage
```

Or use pytest directly:

```bash
# Run all tests
pytest

# Run tests in a specific directory
pytest tests/svg

# Run tests with specific marker
pytest -m unit

# Run a specific test file
pytest tests/unit/test_core.py
```

## Test Markers

The following pytest markers are defined:

- `unit`: Unit tests
- `integration`: Integration tests
- `slow`: Slow tests that might be skipped in quick test runs
- `network`: Tests requiring network access
- `svg`: SVG rendering tests
- `browser`: Browser compatibility tests
- `error_handling`: Error handling tests
- `theme`: Theme support tests
- `export`: Export functionality tests
- `remote`: Remote rendering tests
- `performance`: Performance tests

To mark a test with a specific marker, use the pytest decorator:

```python
import pytest

@pytest.mark.unit
def test_something():
    assert True

@pytest.mark.integration
@pytest.mark.slow
def test_slow_integration():
    # This test is marked as both integration and slow
    assert True
```

## Writing New Tests

When adding new tests:

1. Place them in the appropriate category directory
2. Mark them with the appropriate pytest markers
3. Follow the existing naming patterns
4. Include docstrings explaining the purpose of the test
5. Add any new fixtures to the `conftest.py` file if they're widely used
