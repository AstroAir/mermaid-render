# Mermaid Render Test Suite

This directory contains all the tests for the Mermaid Render library, organized following Python testing best practices.

## Test Organization

The test suite is organized into logical categories for better maintainability and execution:

### Core Test Categories

- **`unit/`**: Unit tests for individual components and modules
  - Tests components in isolation using mocks and stubs
  - Mirrors the source code structure for easy navigation
  - Includes subdirectories for each major module (ai, cache, config, etc.)

- **`integration/`**: Integration tests for component interactions
  - Tests multiple components working together
  - Validates interfaces between modules

- **`e2e/`**: End-to-end tests for complete workflows
  - Tests full user scenarios from start to finish
  - Includes browser compatibility, SVG rendering, export workflows

- **`performance/`**: Performance and benchmark tests
  - Load testing and performance regression detection

- **`regression/`**: Regression tests for bug fixes
  - Ensures previously fixed bugs don't reoccur

### Support Directories

- **`fixtures/`**: Shared test data and fixtures
  - `diagrams/`: Sample diagram files
  - `configs/`: Test configuration files
  - `outputs/`: Expected output files

- **`scripts/`**: Test execution and utility scripts
  - `run_comprehensive_tests.py`: Full test suite runner
  - `run_unit_tests.py`: Unit test runner
  - `run_mcp_tests.py`: MCP-specific test runner

## Running Tests

### Using Make Targets

```bash
# Run all tests
make test

# Run specific test categories
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-e2e          # End-to-end tests only
make test-performance  # Performance tests
make test-regression   # Regression tests

# Run tests with coverage
make test-coverage

# Run fast tests (exclude slow ones)
make test-fast

# Category-specific tests
make test-svg          # SVG rendering tests
make test-browser      # Browser compatibility tests
make test-ai           # AI module tests
make test-cache        # Cache system tests
make test-models       # Model tests
make test-renderers    # Renderer tests
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/e2e/           # End-to-end tests

# Run tests with markers
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m e2e               # End-to-end tests only
pytest -m "not slow"        # Exclude slow tests

# Run specific test files
pytest tests/unit/test_core.py
pytest tests/e2e/test_svg_rendering.py

# Run with coverage
pytest --cov=diagramaid --cov-report=html
```

### Using Test Scripts

```bash
# Comprehensive test runner
python tests/scripts/run_comprehensive_tests.py

# Unit test runner with detailed reporting
python tests/scripts/run_unit_tests.py

# MCP-specific tests
python tests/scripts/run_mcp_tests.py
```

## Test Markers

The following pytest markers are defined for test categorization:

- `unit`: Unit tests
- `integration`: Integration tests
- `e2e`: End-to-end tests
- `slow`: Slow tests that might be skipped in quick runs
- `network`: Tests requiring network access
- `svg`: SVG rendering tests
- `browser`: Browser compatibility tests
- `error_handling`: Error handling tests
- `theme`: Theme support tests
- `export`: Export functionality tests
- `remote`: Remote rendering tests
- `performance`: Performance tests
- `asyncio`: Asynchronous tests

## Writing New Tests

When adding new tests:

1. **Choose the right category**: Place tests in the appropriate directory (unit/integration/e2e)
2. **Follow naming conventions**: Use `test_*.py` for test files
3. **Use appropriate markers**: Mark tests with relevant pytest markers
4. **Mirror source structure**: For unit tests, mirror the source code directory structure
5. **Include docstrings**: Document the purpose and scope of each test
6. **Use fixtures**: Leverage shared fixtures from `conftest.py` and `fixtures/`

## Test Coverage

The test suite provides comprehensive coverage across all major modules:

- ✅ Core functionality (core, cli, convenience, exceptions)
- ✅ AI modules (analysis, compatibility, diagram generation, etc.)
- ✅ Cache system (backends, strategies, performance)
- ✅ Configuration management
- ✅ Model classes (flowchart, sequence, class diagrams, etc.)
- ✅ Renderers (SVG, PNG, PDF, etc.)
- ✅ Templates and utilities
- ✅ Validation and error handling

## Continuous Integration

The test suite is designed to work seamlessly with CI/CD pipelines:

- All tests can be run in parallel using `pytest-xdist`
- Coverage reporting is configured for multiple formats
- Test results are available in JUnit XML format
- Performance benchmarks can be tracked over time
