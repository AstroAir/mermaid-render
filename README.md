# Mermaid Render

[![PyPI version](https://badge.fury.io/py/mermaid-render.svg)](https://badge.fury.io/py/mermaid-render)
[![Python Support](https://img.shields.io/pypi/pyversions/mermaid-render.svg)](https://pypi.org/project/mermaid-render/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/mermaid-render/mermaid-render/workflows/Tests/badge.svg)](https://github.com/mermaid-render/mermaid-render/actions)
[![Coverage](https://codecov.io/gh/mermaid-render/mermaid-render/branch/main/graph/badge.svg)](https://codecov.io/gh/mermaid-render/mermaid-render)

A comprehensive, production-ready Python library for generating Mermaid diagrams with clean APIs, validation, and multiple output formats.

## Features

✨ **Complete Diagram Support**: All major Mermaid diagram types (flowchart, sequence, class, state, ER, etc.)
🎨 **Multiple Output Formats**: SVG, PNG, PDF with high-quality rendering
🔍 **Syntax Validation**: Built-in validation with helpful error messages
🎭 **Theme Management**: Built-in themes plus custom theme support
⚙️ **Flexible Configuration**: Environment variables, config files, runtime options
🛡️ **Type Safety**: Full type hints and mypy compatibility
📚 **Rich Documentation**: Comprehensive docs with examples
🧪 **Thoroughly Tested**: 95%+ test coverage with unit and integration tests

## Quick Start

### Installation

#### Basic Installation

```bash
pip install mermaid-render
```

#### Installation with Optional Features

```bash
# Full installation with all features
pip install mermaid-render[all]

# Specific feature sets
pip install mermaid-render[pdf]           # PDF export support
pip install mermaid-render[cache]         # Redis caching support
pip install mermaid-render[ai]            # AI-powered features
pip install mermaid-render[interactive]   # Interactive web interface
pip install mermaid-render[collaboration] # Collaboration features

# Development installation
pip install mermaid-render[dev]           # Development dependencies
```

#### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, Linux
- **Memory**: Minimum 512MB RAM (2GB+ recommended for AI features)
- **Network**: Internet connection required for online rendering services

#### Optional Dependencies

| Feature | Package | Purpose |
|---------|---------|---------|
| PDF Export | `cairosvg` | Convert SVG to PDF format |
| Redis Cache | `redis` | High-performance caching |
| AI Features | `openai`, `anthropic` | Natural language processing |
| Interactive UI | `fastapi`, `websockets` | Web-based diagram builder |

### Basic Usage

```python
from mermaid_render import MermaidRenderer, FlowchartDiagram

# Create a flowchart
flowchart = FlowchartDiagram()
flowchart.add_node("A", "Start", shape="circle")
flowchart.add_node("B", "Process", shape="rectangle")
flowchart.add_node("C", "End", shape="circle")
flowchart.add_edge("A", "B", label="Begin")
flowchart.add_edge("B", "C", label="Finish")

# Render to SVG
renderer = MermaidRenderer()
svg_content = renderer.render(flowchart, format="svg")

# Save to file
renderer.save(flowchart, "diagram.png", format="png")
```

### 30-Second Tutorial

```python
# 1. Import the library
from mermaid_render import quick_render

# 2. Write your diagram in Mermaid syntax
diagram_code = """
flowchart TD
    A[User Login] --> B{Valid Credentials?}
    B -->|Yes| C[Dashboard]
    B -->|No| D[Error Message]
    D --> A
"""

# 3. Render and save
svg_content = quick_render(diagram_code, "login_flow.svg", theme="dark")
print("✅ Diagram saved as login_flow.svg")
```

### Quick Rendering

```python
from mermaid_render import quick_render

# Render raw Mermaid syntax
diagram_code = """
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
    C --> E[End]
    D --> E
"""

svg_content = quick_render(diagram_code, format="svg", theme="dark")
```

## Supported Diagram Types

| Diagram Type | Class | Description |
|--------------|-------|-------------|
| Flowchart | `FlowchartDiagram` | Process flows and decision trees |
| Sequence | `SequenceDiagram` | Interaction sequences between actors |
| Class | `ClassDiagram` | UML class relationships |
| State | `StateDiagram` | State machines and transitions |
| ER | `ERDiagram` | Entity-relationship diagrams |
| User Journey | `UserJourneyDiagram` | User experience flows |
| Gantt | `GanttDiagram` | Project timelines |
| Pie Chart | `PieChartDiagram` | Data visualization |
| Git Graph | `GitGraphDiagram` | Git branching visualization |
| Mindmap | `MindmapDiagram` | Hierarchical information |

## Examples

### Sequence Diagram

```python
from mermaid_render import SequenceDiagram

sequence = SequenceDiagram(title="User Authentication")
sequence.add_participant("user", "User")
sequence.add_participant("app", "Application")
sequence.add_participant("auth", "Auth Service")

sequence.add_message("user", "app", "Login request")
sequence.add_message("app", "auth", "Validate credentials")
sequence.add_message("auth", "app", "Auth token", message_type="return")
sequence.add_message("app", "user", "Login success", message_type="return")

# Render with custom theme
renderer = MermaidRenderer(theme="dark")
renderer.save(sequence, "auth_flow.svg")
```

### Class Diagram

```python
from mermaid_render import ClassDiagram
from mermaid_render.models.class_diagram import ClassMethod, ClassAttribute

class_diagram = ClassDiagram()

# Add Animal class
animal = class_diagram.add_class("Animal", is_abstract=True)
animal.add_attribute(ClassAttribute("name", "String", "protected"))
animal.add_method(ClassMethod("move", "public", "void", is_abstract=True))

# Add Dog class
dog = class_diagram.add_class("Dog")
dog.add_method(ClassMethod("bark", "public", "void"))

# Add inheritance relationship
class_diagram.add_relationship("Dog", "Animal", "inheritance")

renderer = MermaidRenderer()
renderer.save(class_diagram, "class_hierarchy.svg")
```

### Theme Management

```python
from mermaid_render import MermaidRenderer, MermaidTheme
from mermaid_render.config import ThemeManager

# Use built-in themes
renderer = MermaidRenderer(theme="dark")

# Create custom theme
custom_theme = MermaidTheme("custom",
    primaryColor="#ff6b6b",
    primaryTextColor="#ffffff",
    lineColor="#4ecdc4"
)
renderer.set_theme(custom_theme)

# Manage themes
theme_manager = ThemeManager()
theme_manager.add_custom_theme("corporate", {
    "theme": "corporate",
    "primaryColor": "#2c3e50",
    "primaryTextColor": "#ffffff",
    "lineColor": "#34495e"
})
```

### Validation

```python
from mermaid_render.utils import validate_mermaid_syntax

diagram_code = """
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
"""

result = validate_mermaid_syntax(diagram_code)
if result.is_valid:
    print("✅ Diagram is valid!")
else:
    print("❌ Validation errors:")
    for error in result.errors:
        print(f"  - {error}")
```

### Batch Export

```python
from mermaid_render.utils import export_multiple_formats, batch_export

# Export single diagram to multiple formats
export_multiple_formats(
    my_diagram,
    "output/diagram",
    ["svg", "png", "pdf"]
)

# Export multiple diagrams
diagrams = {
    "flowchart": my_flowchart,
    "sequence": my_sequence,
    "class": my_class_diagram
}

batch_export(diagrams, "output/", format="png", theme="forest")
```

## Configuration

### Environment Variables

```bash
export MERMAID_INK_SERVER="https://mermaid.ink"
export MERMAID_DEFAULT_THEME="dark"
export MERMAID_DEFAULT_FORMAT="svg"
export MERMAID_TIMEOUT=30
export MERMAID_CACHE_ENABLED=true
```

### Configuration File

```python
from mermaid_render.config import ConfigManager

config = ConfigManager(config_file="mermaid_config.json")
config.set("default_theme", "forest")
config.set("timeout", 60)

renderer = MermaidRenderer(config=config)
```

### Runtime Configuration

```python
from mermaid_render import MermaidConfig, MermaidRenderer

config = MermaidConfig(
    timeout=45,
    default_theme="neutral",
    validate_syntax=True,
    cache_enabled=False
)

renderer = MermaidRenderer(config=config)
```

## Advanced Usage

### Custom Renderers

```python
from mermaid_render.renderers import SVGRenderer, PNGRenderer

# Use specific renderers
svg_renderer = SVGRenderer(server_url="http://localhost:8080")
png_renderer = PNGRenderer(width=1200, height=800)

svg_content = svg_renderer.render(diagram_code, theme="dark")
png_data = png_renderer.render(diagram_code, width=1600, height=1200)
```

### Error Handling

```python
from mermaid_render.exceptions import (
    ValidationError,
    RenderingError,
    UnsupportedFormatError
)

try:
    result = renderer.render(diagram, format="svg")
except ValidationError as e:
    print(f"Invalid diagram: {e}")
except RenderingError as e:
    print(f"Rendering failed: {e}")
except UnsupportedFormatError as e:
    print(f"Format not supported: {e}")
```

## System Requirements

### Core Dependencies

- **Python**: 3.8 or higher
- **mermaid-py**: >= 0.8.0 (Mermaid diagram processing)
- **requests**: >= 2.25.0 (HTTP client for rendering services)

### Additional Dependencies for Extended Features

For PDF export support:

```bash
pip install mermaid-render[pdf]  # Installs cairosvg
# OR
pip install cairosvg  # Direct installation
```

For Redis caching:

```bash
pip install mermaid-render[cache]  # Installs redis
# OR
pip install redis  # Direct installation
```

For AI-powered features:

```bash
pip install mermaid-render[ai]  # Installs openai, anthropic
# OR
pip install openai anthropic  # Direct installation
```

## Development

### Setup

```bash
git clone https://github.com/mermaid-render/mermaid-render.git
cd mermaid-render
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mermaid_render --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

### Code Quality

```bash
# Format code
black mermaid_render tests

# Lint code
ruff check mermaid_render tests

# Type checking
mypy mermaid_render
```

## Troubleshooting

### Common Issues

#### Installation Problems

**Issue**: `pip install mermaid-render` fails with dependency conflicts
```bash
# Solution: Use a virtual environment
python -m venv mermaid_env
source mermaid_env/bin/activate  # On Windows: mermaid_env\Scripts\activate
pip install mermaid-render
```

**Issue**: PDF export not working
```bash
# Solution: Install PDF dependencies
pip install mermaid-render[pdf]
# Or manually install cairosvg
pip install cairosvg
```

#### Rendering Issues

**Issue**: "Connection timeout" errors
```python
# Solution: Increase timeout or use local rendering
from mermaid_render import MermaidConfig, MermaidRenderer

config = MermaidConfig(timeout=60)  # Increase timeout
renderer = MermaidRenderer(config=config)
```

**Issue**: "Invalid diagram syntax" errors
```python
# Solution: Use validation to debug
from mermaid_render.utils import validate_mermaid_syntax

result = validate_mermaid_syntax(your_diagram_code)
if not result.is_valid:
    print("Errors found:")
    for error in result.errors:
        print(f"  - {error}")
```

#### Performance Issues

**Issue**: Slow rendering for large diagrams
```python
# Solution: Enable caching
from mermaid_render import MermaidConfig

config = MermaidConfig(cache_enabled=True)
renderer = MermaidRenderer(config=config)
```

### Getting Help

- 📖 **Documentation**: [Full API Documentation](https://mermaid-render.readthedocs.io)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/mermaid-render/mermaid-render/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/mermaid-render/mermaid-render/discussions)
- 📧 **Email**: [support@mermaid-render.dev](mailto:support@mermaid-render.dev)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Set up development environment (`make setup-dev`)
4. Make your changes
5. Add tests for your changes
6. Run quality checks (`make check-all`)
7. Ensure all tests pass (`make test`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

### Development Commands

```bash
# Setup development environment
make setup-dev

# Run tests
make test
make test-coverage

# Code quality
make lint
make format
make type-check

# Build documentation
make docs

# Build package
make build
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Mermaid.js](https://mermaid.js.org/) - The amazing diagramming library
- [mermaid-py](https://github.com/ouhammmourachid/mermaid-py) - Python interface to Mermaid
- [mermaid.ink](https://mermaid.ink/) - Online Mermaid rendering service

## Support

- 📖 [Documentation](https://mermaid-render.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/mermaid-render/mermaid-render/issues)
- 💬 [Discussions](https://github.com/mermaid-render/mermaid-render/discussions)
- 📧 [Email Support](mailto:support@mermaid-render.dev)

---

Made with ❤️ by the Mermaid Render team