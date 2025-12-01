# DiagramAid

[![PyPI version](https://badge.fury.io/py/diagramaid.svg)](https://badge.fury.io/py/diagramaid)
[![Python Support](https://img.shields.io/pypi/pyversions/diagramaid.svg)](https://pypi.org/project/diagramaid/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/AstroAir/diagramaid/workflows/Tests/badge.svg)](https://github.com/AstroAir/diagramaid/actions)
[![Coverage](https://codecov.io/gh/AstroAir/diagramaid/branch/main/graph/badge.svg)](https://codecov.io/gh/AstroAir/diagramaid)

A comprehensive, production-ready Python library for generating Mermaid diagrams with clean APIs, validation, multiple output formats, AI-powered generation, and MCP server integration.

## Features

✨ **Complete Diagram Support**: All major Mermaid diagram types (flowchart, sequence, class, state, ER, journey, gantt, pie, gitgraph, mindmap, timeline)
🎨 **Multiple Output Formats**: SVG, PNG, PDF with high-quality rendering
🔧 **Plugin-Based Architecture**: Extensible renderer system with automatic fallback
🔍 **Enhanced Validation**: Multi-level validation with detailed error reporting
🎭 **Theme Management**: Built-in themes plus custom theme support
⚙️ **Flexible Configuration**: Environment variables, config files, runtime options
🛡️ **Robust Error Handling**: Comprehensive error handling with fallback mechanisms
🚀 **Multiple Rendering Backends**: SVG, PNG, PDF, Playwright, Node.js, and Graphviz renderers
🤖 **AI-Powered Generation**: Natural language to diagram conversion with OpenAI, Anthropic, and OpenRouter
📝 **Template System**: Pre-built templates and data-driven diagram generation
🌐 **Interactive Builder**: Web-based visual diagram builder with real-time preview
🔌 **MCP Server**: Model Context Protocol server for AI assistant integration
📊 **Performance Monitoring**: Built-in caching and performance tracking
🛡️ **Type Safety**: Full type hints and strict mypy compatibility
📚 **Rich Documentation**: Comprehensive docs with examples
🧪 **Thoroughly Tested**: 95%+ test coverage with unit and integration tests

## Quick Start

### Installation

#### Basic Installation

```bash
pip install diagramaid
```

#### Installation with Optional Features

```bash
# Full installation with all features
pip install diagramaid[all]

# Specific feature sets
pip install diagramaid[pdf]           # PDF export support
pip install diagramaid[cache]         # Redis caching support
pip install diagramaid[ai]            # AI-powered features
pip install diagramaid[interactive]   # Interactive web interface


# Development installation
pip install diagramaid[dev]           # Development dependencies

# Enhanced renderer backends (optional)
pip install diagramaid[renderers]     # Playwright and Graphviz renderers
```

#### Enhanced Renderer Installation

For access to additional rendering backends:

```bash
# Install Playwright renderer (high-fidelity browser-based rendering)
pip install playwright
playwright install chromium

# Install Node.js renderer (local Mermaid CLI rendering)
# Requires Node.js: https://nodejs.org/
npm install -g @mermaid-js/mermaid-cli

# Install Graphviz renderer (alternative for flowcharts)
pip install graphviz
# Also install Graphviz system binary: https://graphviz.org/download/
```

#### System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows, macOS, Linux
- **Memory**: Minimum 512MB RAM (2GB+ recommended for AI features)
- **Network**: Internet connection required for online rendering services

#### Optional Dependencies

| Feature | Package | Purpose |
|---------|---------|---------|
| PDF Export | `cairosvg`, `reportlab` | Convert SVG to PDF format |
| Redis Cache | `redis`, `diskcache` | High-performance caching |
| AI Features | `openai`, `anthropic`, `tiktoken` | Natural language processing |
| Interactive UI | `fastapi`, `uvicorn`, `websockets` | Web-based diagram builder |
| Renderers | `playwright`, `graphviz` | Additional rendering backends |
| MCP Server | `fastmcp` | Model Context Protocol server |

### Basic Usage

```python
from diagramaid import MermaidRenderer, FlowchartDiagram

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
from diagramaid import quick_render

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
from diagramaid import quick_render

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
| Timeline | `TimelineDiagram` | Timeline visualization |

## API Reference

### Core Classes

#### MermaidRenderer

The main rendering engine for converting Mermaid diagrams to various output formats.

```python
from diagramaid import MermaidRenderer

renderer = MermaidRenderer(
    theme="default",           # Built-in theme or custom theme
    format="svg",             # Output format: svg, png, pdf
    config=None,              # Custom configuration
    cache_enabled=True        # Enable caching for performance
)

# Render diagram to string
svg_content = renderer.render(diagram)

# Save diagram to file
renderer.save(diagram, "output.svg")

# Render with custom options
renderer.render(diagram, theme="dark", format="png", width=800, height=600)
```

#### Quick Rendering Functions

Convenient functions for simple rendering tasks.

```python
from diagramaid import quick_render, render_to_file

# Render Mermaid code directly
svg_content = quick_render(mermaid_code, format="svg", theme="dark")

# Render and save to file
render_to_file(mermaid_code, "diagram.png", format="png", theme="forest")
```

### Configuration Management

```python
from diagramaid.config import ConfigManager, ThemeManager

# Global configuration
config = ConfigManager()
config.set_default_theme("dark")
config.set_cache_enabled(True)
config.set_output_directory("./diagrams")

# Theme management
theme_manager = ThemeManager()
available_themes = theme_manager.list_themes()
custom_theme = theme_manager.create_theme("my_theme", primaryColor="#ff0000")
```

## Plugin-Based Renderer System

DiagramAid now features a powerful plugin-based architecture that supports multiple rendering backends with automatic fallback capabilities.

### Available Renderers

| Renderer | Description | Formats | Dependencies |
|----------|-------------|---------|--------------|
| **SVG** | Default web-based renderer using mermaid.ink | SVG | requests |
| **PNG** | Web-based PNG renderer | PNG | requests |
| **PDF** | PDF converter from SVG | PDF | cairosvg |
| **Playwright** | High-fidelity browser-based renderer | SVG, PNG, PDF | playwright |
| **Node.js** | Local Mermaid CLI renderer | SVG, PNG, PDF | Node.js + @mermaid-js/mermaid-cli |
| **Graphviz** | Alternative renderer for flowcharts | SVG, PNG, PDF | graphviz |

### Using the Plugin-Based Renderer

```python
from diagramaid import PluginMermaidRenderer

# Create plugin-based renderer with advanced features
renderer = PluginMermaidRenderer()

# Render with automatic renderer selection
svg_content = renderer.render("graph TD\n    A --> B", format="svg")

# Use specific renderer
png_content = renderer.render(
    "graph TD\n    A --> B",
    format="png",
    renderer="playwright"  # Use Playwright for high-fidelity rendering
)

# Enable fallback rendering (default)
result = renderer.render(
    "graph TD\n    A --> B",
    format="svg",
    fallback=True  # Will try multiple renderers if primary fails
)
```

### Renderer Management

```python
# Check available renderers
available = renderer.get_available_renderers()
print(f"Available renderers: {available}")

# Get detailed renderer status
status = renderer.get_renderer_status()
for name, info in status.items():
    print(f"{name}: {'✓' if info['health']['available'] else '✗'}")

# Test specific renderer
test_result = renderer.test_renderer("playwright")
print(f"Playwright test: {test_result['success']}")

# Benchmark all renderers
benchmark = renderer.benchmark_renderers()
```

### Legacy Compatibility Mode

The original MermaidRenderer still works exactly as before:

```python
from diagramaid import MermaidRenderer

# Legacy mode (default)
renderer = MermaidRenderer()
svg_content = renderer.render_raw("graph TD\n    A --> B", format="svg")

# Enable plugin system in legacy renderer
renderer = MermaidRenderer(
    use_plugin_system=True,
    preferred_renderer="playwright"
)
```

## Examples

### Sequence Diagram

```python
from diagramaid import SequenceDiagram

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
from diagramaid import ClassDiagram
from diagramaid.models.class_diagram import ClassMethod, ClassAttribute

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
from diagramaid import MermaidRenderer, MermaidTheme
from diagramaid.config import ThemeManager

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
from diagramaid.utils import validate_mermaid_syntax

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
from diagramaid.utils import export_multiple_formats, batch_export

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

## AI-Powered Features

Generate diagrams from natural language descriptions using multiple AI providers.

### Natural Language to Diagram

```python
from diagramaid.ai import DiagramGenerator, generate_from_text

# Quick generation
diagram = generate_from_text(
    "Create a flowchart showing the user registration process with email verification"
)

# Using DiagramGenerator for more control
generator = DiagramGenerator(provider="openai")  # or "anthropic", "openrouter"
result = generator.from_text(
    "Design a class diagram for an e-commerce system with User, Product, and Order classes",
    diagram_type="class"
)
print(result.diagram_code)
```

### AI Providers

```python
from diagramaid.ai import (
    OpenAIProvider,
    AnthropicProvider,
    OpenRouterProvider,
    ProviderManager
)

# Use specific provider
provider = OpenAIProvider(api_key="your-api-key", model="gpt-4")

# Or use provider manager for automatic fallback
manager = ProviderManager()
manager.add_provider(OpenAIProvider(api_key="..."))
manager.add_provider(AnthropicProvider(api_key="..."))  # Fallback
```

### Diagram Analysis & Optimization

```python
from diagramaid.ai import DiagramAnalyzer, DiagramOptimizer, get_suggestions

# Analyze diagram quality
analyzer = DiagramAnalyzer()
report = analyzer.analyze(my_diagram)
print(f"Complexity: {report.complexity}")
print(f"Quality Score: {report.quality_metrics.overall_score}")

# Get improvement suggestions
suggestions = get_suggestions(my_diagram)
for suggestion in suggestions:
    print(f"[{suggestion.priority}] {suggestion.message}")

# Optimize diagram layout
optimizer = DiagramOptimizer()
optimized = optimizer.optimize_layout(my_diagram)
```

## Template System

Create diagrams from pre-built templates or define custom templates.

### Using Built-in Templates

```python
from diagramaid.templates import TemplateManager, generate_from_template

# List available templates
manager = TemplateManager()
templates = manager.list_templates()
print(templates)  # ['software_architecture', 'user_journey', 'api_sequence', ...]

# Generate from template
diagram = generate_from_template("software_architecture", {
    "title": "My System Architecture",
    "services": [
        {"id": "api", "name": "API Gateway"},
        {"id": "auth", "name": "Auth Service"},
        {"id": "db", "name": "Database"}
    ],
    "databases": [{"id": "postgres", "name": "PostgreSQL"}],
    "connections": [
        {"from": "api", "to": "auth"},
        {"from": "auth", "to": "postgres"}
    ]
})
```

### Template Generators

```python
from diagramaid.templates import (
    FlowchartGenerator,
    SequenceGenerator,
    ClassDiagramGenerator,
    ArchitectureGenerator
)

# Generate flowchart from data
generator = FlowchartGenerator()
flowchart = generator.generate({
    "nodes": [
        {"id": "start", "label": "Start", "type": "circle"},
        {"id": "process", "label": "Process Data", "type": "rectangle"},
        {"id": "end", "label": "End", "type": "circle"}
    ],
    "edges": [
        {"from": "start", "to": "process"},
        {"from": "process", "to": "end"}
    ]
})
```

### Data Sources

```python
from diagramaid.templates import JSONDataSource, CSVDataSource, DatabaseDataSource

# Load data from JSON
json_source = JSONDataSource("data/architecture.json")
data = json_source.load()

# Load from CSV
csv_source = CSVDataSource("data/nodes.csv")
nodes = csv_source.load()

# Load from database
db_source = DatabaseDataSource(connection_string="postgresql://...")
data = db_source.query("SELECT * FROM diagram_data")
```

## Interactive Web Builder

Build diagrams visually with real-time preview and collaboration features.

### Starting the Interactive Server

```python
from diagramaid.interactive import DiagramBuilder, start_server

# Create builder and start server
builder = DiagramBuilder()
start_server(builder, host="localhost", port=8080)

# Access at http://localhost:8080
```

### Programmatic Usage

```python
from diagramaid.interactive import (
    DiagramBuilder,
    create_interactive_session,
    export_diagram_code
)

# Create a session
session = create_interactive_session()

# Build diagram programmatically
builder = DiagramBuilder()
builder.add_element("node", id="A", label="Start", position=(100, 100))
builder.add_element("node", id="B", label="Process", position=(100, 200))
builder.add_connection("A", "B", label="next")

# Export to Mermaid code
code = export_diagram_code(builder)
print(code)
```

## MCP Server Integration

Expose diagramaid capabilities through the Model Context Protocol for AI assistant integration.

### Running the MCP Server

```bash
# Start MCP server
diagramaid-mcp

# Or programmatically
python -m diagramaid.mcp
```

### MCP Configuration

Add to your Claude Desktop or other MCP client configuration:

```json
{
  "mcpServers": {
    "diagramaid": {
      "command": "diagramaid-mcp",
      "args": []
    }
  }
}
```

### Available MCP Tools

The MCP server exposes these tool categories:

**Core Tools:**

- `render_diagram` - Render Mermaid diagrams to SVG/PNG/PDF
- `validate_diagram` - Validate diagram syntax and structure
- `list_themes` - List available themes

**AI-Powered Tools:**

- `generate_diagram_from_text` - Generate diagrams from natural language
- `optimize_diagram` - Optimize diagram layout and structure
- `analyze_diagram` - Analyze diagram quality and complexity

**Template Tools:**

- `create_from_template` - Create diagrams from templates
- `list_available_templates` - List available templates

**Extended Tools:**

- `convert_diagram_format` - Convert between output formats
- `merge_diagrams` - Merge multiple diagrams
- `export_to_markdown` - Export with documentation

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
from diagramaid.config import ConfigManager

config = ConfigManager(config_file="mermaid_config.json")
config.set("default_theme", "forest")
config.set("timeout", 60)

renderer = MermaidRenderer(config=config)
```

### Runtime Configuration

```python
from diagramaid import MermaidConfig, MermaidRenderer

config = MermaidConfig(
    timeout=45,
    default_theme="neutral",
    validate_syntax=True,
    cache_enabled=False
)

renderer = MermaidRenderer(config=config)
```

## Architecture

The DiagramAid library is designed with a modular, plugin-based architecture that promotes code reusability, maintainability, and extensibility.

### Core Modules

- **`core.py`** - Core classes (`MermaidRenderer`, `MermaidConfig`, `MermaidDiagram`)
- **`models/`** - Object-oriented diagram models for type-safe diagram creation
- **`renderers/`** - Plugin-based rendering system with multiple backends
- **`validators/`** - Comprehensive validation system with detailed error reporting
- **`config/`** - Advanced configuration management with file and environment support
- **`utils/`** - Utility functions and helper classes
- **`convenience.py`** - High-level convenience functions for simple use cases

### Optional Feature Modules

- **`ai/`** - AI-powered diagram generation and optimization
- **`interactive/`** - Web-based interactive diagram builder
- **`mcp/`** - Model Context Protocol server for AI assistant integration
- **`templates/`** - Template system for generating diagrams from data
- **`cache/`** - Caching system with multiple backends

### Plugin System

The library uses a plugin-based architecture for rendering, allowing you to:

- Choose from multiple rendering backends (Playwright, Node.js, Graphviz)
- Add custom renderers without modifying core code
- Configure renderer-specific settings independently
- Fallback gracefully between renderers

### Design Principles

1. **Modularity**: Each module has a single, clear responsibility
2. **Plugin Architecture**: Extensible through plugins rather than core modifications
3. **Type Safety**: Full type hints and runtime validation
4. **Backward Compatibility**: Changes maintain existing APIs
5. **Performance**: Efficient caching and shared resource management
6. **Documentation**: Every module includes comprehensive README files

## Advanced Usage

### Custom Renderers

```python
from diagramaid.renderers import SVGRenderer, PNGRenderer

# Use specific renderers
svg_renderer = SVGRenderer(server_url="http://localhost:8080")
png_renderer = PNGRenderer(width=1200, height=800)

svg_content = svg_renderer.render(diagram_code, theme="dark")
png_data = png_renderer.render(diagram_code, width=1600, height=1200)
```

### Error Handling

```python
from diagramaid.exceptions import (
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

- **Python**: 3.10 or higher
- **mermaid-py**: >= 0.8.0 (Mermaid diagram processing)
- **requests**: >= 2.25.0 (HTTP client for rendering services)
- **jinja2**: >= 3.0.0 (Template rendering)
- **jsonschema**: >= 4.0.0 (Schema validation)

### Additional Dependencies for Extended Features

For PDF export support:

```bash
pip install diagramaid[pdf]  # Installs cairosvg, reportlab
# OR
pip install cairosvg reportlab  # Direct installation
```

For Redis caching:

```bash
pip install diagramaid[cache]  # Installs redis, diskcache
# OR
pip install redis diskcache  # Direct installation
```

For AI-powered features:

```bash
pip install diagramaid[ai]  # Installs openai, anthropic, tiktoken
# OR
pip install openai anthropic tiktoken  # Direct installation
```

For interactive web builder:

```bash
pip install diagramaid[interactive]  # Installs fastapi, uvicorn, websockets
```

For additional rendering backends:

```bash
pip install diagramaid[renderers]  # Installs playwright, graphviz
```

## Development

### Setup

```bash
git clone https://github.com/AstroAir/diagramaid.git
cd diagramaid
pip install -e ".[dev]"

# Or use make for complete setup
make setup-dev
```

### Testing

```bash
# Run all tests with coverage
make test

# Or using pytest directly
pytest

# Run with coverage report
pytest --cov=diagramaid --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
make test-fast          # Quick tests via make

# Run specific test file or function
pytest tests/unit/test_core.py
pytest -k "test_flowchart_basic"
```

### Code Quality

```bash
# Format code
make format
# Or directly
black diagramaid tests
ruff format diagramaid tests

# Lint code
make lint
# Or directly
ruff check diagramaid tests

# Type checking
make type-check
# Or directly
mypy diagramaid

# Run all quality checks
make check-all
```

## Troubleshooting

### Common Issues

#### Installation Problems

**Issue**: `pip install diagramaid` fails with dependency conflicts

```bash
# Solution: Use a virtual environment
python -m venv mermaid_env
source mermaid_env/bin/activate  # On Windows: mermaid_env\Scripts\activate
pip install diagramaid
```

**Issue**: PDF export not working

```bash
# Solution: Install PDF dependencies
pip install diagramaid[pdf]
# Or manually install cairosvg
pip install cairosvg
```

#### Rendering Issues

**Issue**: "Connection timeout" errors

```python
# Solution: Increase timeout or use local rendering
from diagramaid import MermaidConfig, MermaidRenderer

config = MermaidConfig(timeout=60)  # Increase timeout
renderer = MermaidRenderer(config=config)
```

**Issue**: "Invalid diagram syntax" errors

```python
# Solution: Use validation to debug
from diagramaid.utils import validate_mermaid_syntax

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
from diagramaid import MermaidConfig

config = MermaidConfig(cache_enabled=True)
renderer = MermaidRenderer(config=config)
```

#### AI Features Issues

**Issue**: AI generation not working

```python
# Solution: Ensure API keys are configured
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
# Or for Anthropic
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"
```

**Issue**: MCP server not starting

```bash
# Solution: Ensure fastmcp is installed
pip install diagramaid[all]
# Or install fastmcp directly
pip install fastmcp
```

#### Renderer Issues

**Issue**: Playwright renderer not available

```bash
# Solution: Install Playwright and browser
pip install playwright
playwright install chromium
```

**Issue**: Graphviz renderer not working

```bash
# Solution: Install both Python package and system binary
pip install graphviz
# Then install system binary from https://graphviz.org/download/
```

### Getting Help

- 📖 **Documentation**: [Full API Documentation](https://diagramaid.readthedocs.io)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AstroAir/diagramaid/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/AstroAir/diagramaid/discussions)
- 📧 **Email**: [astro_air@126.com](mailto:astro_air@126.com)

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
- [mermaid.ink](https://mermaid.ink/) - Online DiagramAiding service
- [FastMCP](https://github.com/jlowin/fastmcp) - Model Context Protocol framework

## Support

- 📖 [Documentation](https://diagramaid.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/AstroAir/diagramaid/issues)
- 💬 [Discussions](https://github.com/AstroAir/diagramaid/discussions)
- 📧 [Email Support](mailto:astro_air@126.com)

---

Made with ❤️ by Max Qian
