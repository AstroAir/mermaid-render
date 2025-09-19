# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Mermaid Render is a comprehensive, production-ready Python library for generating Mermaid diagrams with clean APIs, validation, and multiple output formats. The project uses a plugin-based architecture that supports multiple rendering backends with automatic fallback capabilities.

## Development Commands

### Environment Setup
```bash
# Complete development environment setup
make setup-dev

# Basic development installation
pip install -e ".[dev,cache,interactive,ai,collaboration,docs]"

# Install specific feature sets
pip install -e ".[all]"  # Full installation with all features
```

### Testing
```bash
# Run all tests
make test
pytest

# Run specific test categories
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-fast          # Exclude slow tests
make test-coverage      # Tests with coverage report

# Category-specific tests
make test-svg           # SVG rendering tests
make test-browser       # Browser compatibility tests
make test-error-handling # Error handling tests
make test-theme         # Theme support tests
make test-export        # Export functionality tests
make test-remote        # Remote rendering tests
make test-performance   # Performance tests

# Verbose testing
pytest -v
pytest --cov=mermaid_render --cov-report=html
```

### Code Quality
```bash
# Format code
make format
black mermaid_render tests examples

# Lint code
make lint
ruff check mermaid_render tests

# Type checking
make type-check
mypy mermaid_render

# Run all quality checks
make check-all
```

### Build and Release
```bash
# Clean build artifacts
make clean

# Build package
make build
python -m build

# Release to PyPI (requires authentication)
make release
```

### Utilities
```bash
# Run demo script
make demo
python demo.py

# Security checks
make security
safety check
bandit -r mermaid_render/

# Update dependencies
make deps-update
uv lock --upgrade

# Performance benchmarks
make benchmark

# Environment information
make env-info
```

## Architecture Overview

### Core Components

#### Plugin-Based Renderer System
The library features a sophisticated plugin-based architecture located in `mermaid_render/renderers/`:

- **SVG Renderer** (`svg_renderer.py`) - Default web-based renderer using mermaid.ink
- **PNG Renderer** (`png_renderer.py`) - Web-based PNG renderer
- **PDF Renderer** (`pdf_renderer.py`) - PDF converter from SVG using cairosvg
- **Playwright Renderer** (`playwright_renderer.py`) - High-fidelity browser-based renderer
- **Node.js Renderer** (`nodejs_renderer.py`) - Local Mermaid CLI renderer
- **Graphviz Renderer** (`graphviz_renderer.py`) - Alternative renderer for flowcharts

#### Core Classes (`core.py`)
- **MermaidRenderer** - Main rendering engine with fallback support
- **EnhancedMermaidRenderer** - Advanced renderer with plugin system integration
- **MermaidConfig** - Centralized configuration management
- **MermaidTheme** - Theme configuration and management

#### Diagram Models (`models/`)
Object-oriented diagram models for type-safe diagram creation:
- `FlowchartDiagram` - Process flows and decision trees
- `SequenceDiagram` - Interaction sequences between actors
- `ClassDiagram` - UML class relationships
- `StateDiagram` - State machines and transitions
- `ERDiagram` - Entity-relationship diagrams
- And 6 more diagram types

#### Optional Feature Modules
- **AI Module** (`ai/`) - AI-powered diagram generation and optimization
- **Interactive Module** (`interactive/`) - Web-based interactive diagram builder

- **Templates Module** (`templates/`) - Template system for generating diagrams from data
- **Cache Module** (`cache/`) - Caching system with multiple backends (Redis, file, memory)

### Key Design Principles

1. **Plugin Architecture** - Extensible renderer system with automatic fallback
2. **Type Safety** - Full type hints throughout the codebase
3. **Configuration Hierarchy** - Environment variables → config files → runtime parameters
4. **Modular Optional Features** - Core functionality separate from optional features
5. **Comprehensive Error Handling** - Detailed error reporting and graceful degradation

## Development Workflow

### Setting Up New Features
When adding new diagram types or renderers:
1. Follow the base class patterns in `models/` or `renderers/base.py`
2. Add comprehensive type hints
3. Include validation logic
4. Add tests in the appropriate `tests/` subdirectory
5. Update the `__init__.py` exports

### Testing Strategy
The project uses pytest with comprehensive test markers:
- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests with external dependencies
- `@pytest.mark.slow` - Time-intensive tests
- `@pytest.mark.network` - Tests requiring network access

### Configuration Management
The configuration system follows a hierarchical approach:
1. Default values (in `MermaidConfig.__init__`)
2. Environment variables (prefix: `MERMAID_`)
3. Configuration files
4. Runtime parameters (highest priority)

### Plugin System Development
When developing new renderers:
- Inherit from `BaseRenderer` in `renderers/base.py`
- Implement health checks and performance metrics
- Support graceful fallback mechanisms
- Register with the `RendererRegistry`

## Entry Points

### Command Line Interface
```bash
mermaid-render input.mmd -o output.svg -f svg -t dark
```

### Python API Entry Points
- `quick_render()` - Simple rendering function
- `MermaidRenderer` - Standard renderer with basic plugin support
- `EnhancedMermaidRenderer` - Full plugin system with advanced features
- Diagram classes in `mermaid_render.models`

### Library Integration Points
- CLI: `mermaid_render.cli:main`
- Convenience functions: `mermaid_render.convenience`
- Plugin system: `mermaid_render.plugin_renderer`

## Common Development Tasks

### Adding a New Diagram Type
1. Create new module in `models/` following existing patterns
2. Inherit from `MermaidDiagram` base class
3. Implement `to_mermaid()` method for code generation
4. Add validation logic in `validators/`
5. Export in `models/__init__.py` and main `__init__.py`

### Adding a New Renderer
1. Create renderer in `renderers/` inheriting from `BaseRenderer`
2. Implement required methods: `render()`, `health_check()`, `get_capabilities()`
3. Register in `RendererRegistry`
4. Add configuration options in `RendererConfig`
5. Include comprehensive error handling

### Performance Optimization
- Use the caching system for expensive operations
- Implement batch operations for multiple diagrams
- Monitor performance with the built-in `PerformanceMonitor`
- Consider renderer selection based on diagram complexity

## File Structure Significance

- `core.py` - Central classes that all other modules depend on
- `plugin_renderer.py` - Modern plugin-based rendering system
- `convenience.py` - High-level functions for simple use cases
- `exceptions.py` - Comprehensive error hierarchy
- `models/` - Type-safe diagram creation APIs
- `renderers/` - Pluggable rendering backends
- `validators/` - Multi-level validation system
- `config/` - Configuration and theme management

The modular architecture allows features to be installed independently via optional dependencies (`pip install mermaid-render[cache,ai,interactive]`).
