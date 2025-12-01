# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DiagramAid is a production-ready Python library for generating Mermaid diagrams with a plugin-based architecture supporting multiple rendering backends, comprehensive validation, AI integration, and MCP server capabilities.

## Development Commands

### Essential Commands (via Makefile or scripts/dev.py)

```bash
# Setup
make setup-dev              # Complete dev environment setup
make install-dev            # Install with all dev dependencies

# Testing
make test                   # Run all tests with coverage
make test-unit              # Unit tests only
make test-integration       # Integration tests only
make test-fast              # Skip slow tests
pytest -m unit              # Direct pytest with markers
pytest tests/unit/ai/       # Test specific module
pytest -k "test_name"       # Run specific test

# Code Quality
make format                 # Format with black and ruff
make lint                   # Run linting checks
make type-check             # Run mypy type checking
make check-all              # Run all quality checks
make security               # Security checks (bandit, safety)

# Build & Clean
make build                  # Build package
make clean                  # Clean build artifacts

# Using dev.py directly
python scripts/dev.py test
python scripts/dev.py all   # All quality checks
python scripts/dev.py format
```

### Running Single Tests

```bash
# By file
pytest tests/unit/test_core.py

# By test name
pytest -k "test_flowchart_basic"

# By marker
pytest -m "unit and not slow"

# With verbose output
pytest -vv tests/unit/renderers/test_base.py
```

## Architecture Overview

### Core Layer Structure

**Entry Points:**
- `diagramaid/__init__.py` - Main public API exports
- `diagramaid/core.py` - Core classes (MermaidRenderer, MermaidConfig, MermaidDiagram)
- `diagramaid/plugin_renderer.py` - Plugin-based renderer system (PluginMermaidRenderer)
- `diagramaid/convenience.py` - Quick rendering functions (quick_render, render_to_file)

**Diagram Models** (`diagramaid/models/`):
- 10+ diagram types: Flowchart, Sequence, Class, State, ER, Journey, Gantt, Pie, GitGraph, Mindmap, Timeline
- Each model provides type-safe construction, validation, and Mermaid syntax generation
- Base class: `MermaidDiagram` with caching and validation hooks

**Rendering System** (`diagramaid/renderers/`):
- `base.py` - Abstract BaseRenderer with template method pattern
- `registry.py` - RendererRegistry for plugin registration and discovery
- `manager.py` - RendererManager orchestrates fallback chains and renderer selection
- Concrete renderers: SVG, PNG, PDF, Playwright, Node.js, Graphviz
- Each renderer declares capabilities (formats, features) and health status

**Infrastructure:**
- `validators/` - Multi-level validation (syntax, structural, semantic, best practice)
- `cache/` - Multi-backend caching (Memory, File, Redis) with unified interface
- `config/` - Hierarchical configuration (runtime > env vars > config files > defaults)
- `utils/` - Export utilities, validation helpers, format detection

**Optional Modules:**
- `ai/` - AI-powered diagram generation (OpenAI, Anthropic, OpenRouter providers)
- `interactive/` - FastAPI web builder with WebSocket collaboration
- `mcp/` - Model Context Protocol server for Claude integration
- `templates/` - Template-based diagram generation from data

### Key Architectural Patterns

1. **Plugin Registry Pattern**: Renderers register themselves with RendererRegistry, enabling runtime discovery and dynamic fallback chains
2. **Chain of Responsibility**: RendererManager tries multiple renderers in sequence if primary fails
3. **Template Method**: BaseRenderer defines rendering skeleton; subclasses implement specifics
4. **Factory**: RendererRegistry creates renderer instances based on requirements
5. **Strategy**: Different cache backends and AI providers implement common interfaces
6. **Facade**: MermaidRenderer simplifies complex plugin system for basic use cases

### Module Interaction Flow

```
User Code
  ↓
MermaidRenderer (facade) or PluginMermaidRenderer
  ↓
RendererManager (orchestration)
  ↓
RendererRegistry (discovery) → BaseRenderer implementations
  ↓
Validation → Caching → Actual rendering backend
```

## Important Implementation Notes

### Type Safety & Mypy Configuration

- **Strict mode enabled** with practical `Any` usage allowed (`disallow_any_expr = false`)
- This is intentional for handling dynamic data (JSON, API responses, config dicts)
- All core code must have type hints; `Any` is acceptable for dynamic contexts
- Run `make type-check` before committing

### Testing Organization

Tests mirror source structure under `tests/`:
- `unit/` - Mirrors `diagramaid/` structure (e.g., `unit/ai/`, `unit/renderers/`)
- `integration/` - Multi-component interaction tests
- `e2e/` - Full workflow tests
- `performance/` - Benchmarks and load tests
- `regression/` - Bug fix regression tests
- `fixtures/` - Shared test data

Use markers: `@pytest.mark.unit`, `@pytest.mark.slow`, `@pytest.mark.network`, etc.

### Renderer System

When adding new renderers:
1. Inherit from `BaseRenderer` in `renderers/base.py`
2. Implement `_render_diagram()` method
3. Declare capabilities via `Capability` enum
4. Register in `renderers/__init__.py`
5. Add health check logic
6. Update renderer tests in `tests/unit/renderers/`

### Environment Variables

```bash
MERMAID_INK_SERVER     # Default: https://mermaid.ink
MERMAID_DEFAULT_THEME  # Default: default
MERMAID_DEFAULT_FORMAT # Default: svg
MERMAID_TIMEOUT        # Default: 30 seconds
MERMAID_CACHE_ENABLED  # Default: true
```

### Recent Cleanup (Important Context)

The project recently underwent major cleanup:
- Removed `performance.py` module from cache - do NOT import PerformanceMonitor
- Removed `Capability.PERFORMANCE_METRICS` from renderers
- Deleted standalone validation/logging modules in renderers/
- Consolidated tests into organized structure
- All imports now validate during build - check with `python scripts/dev.py test`

### AI Module Architecture

The AI system (`diagramaid/ai/`) uses:
- `providers.py` - Abstract AIProvider with OpenAI/Anthropic/OpenRouter implementations
- `diagram_generator.py` - Natural language → Mermaid conversion
- `compatibility.py` - Feature detection and provider capability checking
- Provider selection is automatic based on available API keys

### MCP Server Integration

The MCP server (`diagramaid/mcp/`) exposes tools to Claude:
- Rendering, validation, generation, theme management, batch export
- Entry point: `diagramaid.mcp_server:main`
- Resources expose templates and themes
- Prompts provide diagram type examples

## Development Workflow

### Making Changes

1. **Before coding**: Run `make setup-dev` to ensure environment is ready
2. **During development**: Run `make test-fast` for quick validation
3. **Before committing**: Run `make check-all` (format, lint, type-check, test)
4. **Adding features**: Update tests first, ensure 95%+ coverage maintained

### Code Quality Standards

- **Black** for formatting (line length: 88)
- **Ruff** for linting (select: E, W, F, I, B, C4, UP)
- **Mypy** for type checking (strict mode with practical Any usage)
- **Pytest** for testing with markers and parallel execution

### Cross-Platform Considerations

All scripts support Windows, macOS, and Linux:
- Use `scripts/setup-dev.py` (not shell-specific commands)
- Use `Path` from `pathlib` for file paths
- Test on Windows if modifying scripts or file I/O

## Performance Considerations

- Caching is critical: Enable by default, use appropriate backend
- Lazy loading for optional features (AI, interactive builder)
- Plugin system allows renderer selection based on performance needs
- Run benchmarks with `python scripts/benchmark.py` when optimizing

## Common Pitfall Avoidance

1. **Don't import deleted modules**: No `performance.py`, no `validation.py` in renderers/
2. **Use correct validator API**: `validator.validate()` returns `ValidationResult`, not boolean
3. **Template validation**: Import `validate_template_parameters` from `schema.py`, not `utils.py`
4. **Renderer capabilities**: Use current `Capability` enum values, check `renderers/base.py`
5. **Test organization**: Mirror source structure in `tests/unit/`, use appropriate markers
6. **Type hints**: Required everywhere; use `Any` judiciously for dynamic data

## Documentation

- Each module has its own README.md (see `renderers/README.md`, `tests/README.md`, etc.)
- API documentation uses docstrings (Google style)
- Architecture docs in this file and main README.md
- For detailed examples, see README.md sections

## Build & Release

```bash
# Build package
make build                 # Creates dist/ with wheel and sdist

# Version management
python scripts/version_manager.py bump --type minor

# Package validation
python scripts/validate-package.py

# Release (requires PyPI credentials)
make release
```
