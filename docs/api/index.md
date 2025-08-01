# API Reference

This section provides comprehensive documentation for all public APIs in the Mermaid Render library. The API is designed to be intuitive and powerful, supporting both simple use cases and advanced scenarios.

## Quick Reference

### Essential Imports
```python
# Core functionality
from mermaid_render import MermaidRenderer, MermaidConfig, MermaidTheme

# Diagram types
from mermaid_render import (
    FlowchartDiagram, SequenceDiagram, ClassDiagram,
    StateDiagram, ERDiagram, GanttDiagram
)

# Utilities
from mermaid_render import quick_render, export_to_file
from mermaid_render.utils import validate_mermaid_syntax
```

### Common Patterns
```python
# Basic rendering
renderer = MermaidRenderer()
svg_content = renderer.render(diagram, format="svg")

# With configuration
config = MermaidConfig(timeout=60, validate_syntax=True)
renderer = MermaidRenderer(config=config, theme="dark")

# Quick rendering from string
svg_content = quick_render(mermaid_code, theme="forest")
```

## Core Classes

### MermaidRenderer
The main rendering engine for converting Mermaid diagrams to various output formats.

This is the primary interface for rendering operations. It handles the complete rendering
pipeline including validation, theme application, format conversion, and caching.

```python
from mermaid_render import MermaidRenderer, MermaidConfig

# Basic usage
renderer = MermaidRenderer()

# With custom configuration
config = MermaidConfig(timeout=60, cache_enabled=True)
renderer = MermaidRenderer(config=config, theme="dark")

# Render diagram
result = renderer.render(diagram, format="svg")
```

#### Constructor
```python
MermaidRenderer(
    config: Optional[MermaidConfig] = None,
    theme: Optional[Union[str, MermaidTheme]] = None
)
```

**Parameters:**
- `config`: Configuration object with rendering settings. If None, default configuration is used
- `theme`: Theme name (string) or MermaidTheme object. Available built-in themes: "default", "dark", "forest", "neutral", "base"

#### Methods

##### render()
```python
render(
    diagram: Union[MermaidDiagram, str],
    format: str = "svg",
    **options: Any
) -> str
```

Render a diagram to the specified format.

**Parameters:**
- `diagram`: MermaidDiagram object or raw Mermaid syntax string
- `format`: Output format ("svg", "png", "pdf")
- `**options`: Additional rendering options:
  - `width`: Output width in pixels (for raster formats)
  - `height`: Output height in pixels (for raster formats)
  - `background`: Background color (default: transparent)
  - `scale`: Scale factor for output size

**Returns:** Rendered diagram content as string (SVG) or bytes (PNG/PDF)

**Raises:**
- `ValidationError`: If diagram syntax is invalid
- `RenderingError`: If rendering process fails
- `UnsupportedFormatError`: If format is not supported

**Example:**
```python
# Render diagram object
flowchart = FlowchartDiagram()
flowchart.add_node("A", "Start")
svg_content = renderer.render(flowchart, format="svg")

# Render with options
png_data = renderer.render(
    flowchart,
    format="png",
    width=1200,
    height=800,
    background="#ffffff"
)

# Render raw Mermaid code
mermaid_code = "graph TD; A-->B"
result = renderer.render(mermaid_code, format="svg")
```

##### render_raw()
```python
render_raw(
    mermaid_code: str,
    format: str = "svg",
    **options: Any
) -> str
```

Render raw Mermaid code directly without diagram object validation.

**Parameters:**
- `mermaid_code`: Raw Mermaid diagram syntax
- `format`: Output format
- `**options`: Additional rendering options

**Returns:** Rendered content

**Example:**
```python
code = """
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[End]
"""
svg_content = renderer.render_raw(code, format="svg")
```

##### save()
```python
save(
    diagram: Union[MermaidDiagram, str],
    output_path: Union[str, Path],
    format: Optional[str] = None,
    **options: Any
) -> None
```

Render and save diagram to file.

**Parameters:**
- `diagram`: Diagram to render
- `output_path`: Output file path
- `format`: Output format (auto-detected from extension if None)
- `**options`: Additional rendering options

**Example:**
```python
# Save with auto-detected format
renderer.save(diagram, "output.svg")

# Save with explicit format
renderer.save(diagram, "output", format="png")

# Save with options
renderer.save(
    diagram,
    "high_res.png",
    format="png",
    width=2400,
    height=1600
)
```

##### set_theme()
```python
set_theme(theme: Union[str, MermaidTheme]) -> None
```

Set the rendering theme.

**Parameters:**
- `theme`: Theme name or MermaidTheme object

**Example:**
```python
# Set built-in theme
renderer.set_theme("dark")

# Set custom theme
custom_theme = MermaidTheme("custom", primaryColor="#ff6b6b")
renderer.set_theme(custom_theme)
```

##### get_theme()
```python
get_theme() -> Optional[MermaidTheme]
```

Get the current theme.

**Returns:** Current MermaidTheme object or None

##### Class Attributes
- `SUPPORTED_FORMATS`: List of supported output formats

### MermaidDiagram
Base class for all diagram types. Provides common functionality for diagram creation and validation.

```python
from mermaid_render import FlowchartDiagram

diagram = FlowchartDiagram(title="My Flowchart")
mermaid_code = diagram.to_mermaid()
```

**Methods:**
- `to_mermaid()` - Generate Mermaid syntax string
- `validate()` - Validate diagram structure
- `add_metadata(key, value)` - Add custom metadata
- `get_complexity_score()` - Get diagram complexity metric

### MermaidConfig
Configuration management for the library.

```python
from mermaid_render import MermaidConfig

config = MermaidConfig(
    timeout=30,
    default_theme="dark",
    validate_syntax=True
)
```

**Properties:**
- `timeout` - Request timeout in seconds
- `default_theme` - Default theme name
- `validate_syntax` - Enable/disable syntax validation
- `server_url` - Rendering server URL
- `cache_enabled` - Enable/disable caching

### MermaidTheme
Theme management for customizing diagram appearance.

```python
from mermaid_render import MermaidTheme

theme = MermaidTheme(
    name="custom",
    primaryColor="#ff6b6b",
    primaryTextColor="#ffffff"
)
```

## Diagram Types

### FlowchartDiagram
Create flowchart diagrams with nodes and edges.

```python
from mermaid_render import FlowchartDiagram

flowchart = FlowchartDiagram(direction="TD")
flowchart.add_node("A", "Start", shape="circle")
flowchart.add_edge("A", "B", label="Next")
```

**Methods:**
- `add_node(id, label, shape="rectangle", **kwargs)` - Add a node
- `add_edge(from_id, to_id, label=None, **kwargs)` - Add an edge
- `add_subgraph(id, title, nodes)` - Add a subgraph
- `set_direction(direction)` - Set flow direction

### SequenceDiagram
Create sequence diagrams showing interactions between participants.

```python
from mermaid_render import SequenceDiagram

sequence = SequenceDiagram(title="API Call")
sequence.add_participant("client", "Client")
sequence.add_message("client", "server", "Request")
```

**Methods:**
- `add_participant(id, name=None)` - Add a participant
- `add_message(from_id, to_id, message, type="sync")` - Add a message
- `add_note(text, participant, position="right of")` - Add a note
- `add_activation(participant)` - Add activation box

### ClassDiagram
Create UML class diagrams.

```python
from mermaid_render import ClassDiagram
from mermaid_render.models.class_diagram import ClassMethod, ClassAttribute

class_diagram = ClassDiagram()
animal = class_diagram.add_class("Animal")
animal.add_method(ClassMethod("move", "public", "void"))
```

**Methods:**
- `add_class(name, is_abstract=False)` - Add a class
- `add_relationship(from_class, to_class, type)` - Add relationship
- `add_interface(name)` - Add an interface
- `add_enum(name, values)` - Add an enumeration

### StateDiagram
Create state machine diagrams.

```python
from mermaid_render import StateDiagram

state = StateDiagram()
state.add_state("idle", "Idle State")
state.add_transition("idle", "active", "start")
```

**Methods:**
- `add_state(id, label=None)` - Add a state
- `add_transition(from_state, to_state, trigger=None)` - Add transition
- `add_composite_state(id, substates)` - Add composite state
- `set_initial_state(state_id)` - Set initial state

## Utility Functions

### Validation
```python
from mermaid_render.utils import validate_mermaid_syntax

result = validate_mermaid_syntax(diagram_code)
if result.is_valid:
    print("Valid diagram!")
else:
    print("Errors:", result.errors)
```

### Export Utilities
```python
from mermaid_render.utils import export_to_file, export_multiple_formats

# Export single format
export_to_file(diagram, "output.svg", format="svg")

# Export multiple formats
export_multiple_formats(diagram, "output", ["svg", "png", "pdf"])
```

### Theme Utilities
```python
from mermaid_render.utils import get_available_themes, get_supported_formats

themes = get_available_themes()
formats = get_supported_formats()
```

## Configuration Management

### ThemeManager
```python
from mermaid_render.config import ThemeManager

theme_manager = ThemeManager()
theme_manager.add_custom_theme("corporate", theme_config)
available_themes = theme_manager.get_available_themes()
```

### ConfigManager
```python
from mermaid_render.config import ConfigManager

config_manager = ConfigManager(config_file="config.json")
config_manager.set("default_theme", "dark")
config = config_manager.get_config()
```

## Advanced Features

### Template System
```python
from mermaid_render.templates import TemplateManager, FlowchartGenerator

template_manager = TemplateManager()
generator = FlowchartGenerator()
diagram = generator.generate_process_flow(steps)
```

### Caching System
```python
from mermaid_render.cache import CacheManager, create_cache_manager

cache = create_cache_manager("redis", host="localhost")
cache.warm_cache(diagrams)
stats = cache.get_stats()
```

### Interactive Features
```python
from mermaid_render.interactive import DiagramBuilder, start_server

builder = DiagramBuilder()
server = start_server(port=8080)
```

### AI Features
```python
from mermaid_render.ai import generate_from_text, optimize_diagram

diagram = generate_from_text("Create a user login flow")
optimized = optimize_diagram(diagram)
```

## Error Handling

### Exception Types
```python
from mermaid_render.exceptions import (
    ValidationError,
    RenderingError,
    ConfigurationError,
    UnsupportedFormatError
)

try:
    result = renderer.render(diagram)
except ValidationError as e:
    print(f"Validation failed: {e}")
except RenderingError as e:
    print(f"Rendering failed: {e}")
```

## Type Hints

The library provides comprehensive type hints for better IDE support:

```python
from typing import Optional, List, Dict, Any
from mermaid_render import MermaidRenderer, FlowchartDiagram

def create_workflow(steps: List[str]) -> FlowchartDiagram:
    diagram = FlowchartDiagram()
    # Implementation
    return diagram

def render_diagram(
    diagram: MermaidDiagram,
    format: str = "svg",
    theme: Optional[str] = None
) -> str:
    renderer = MermaidRenderer()
    return renderer.render(diagram, format=format)
```

## Performance Considerations

### Optimization Tips
- Use caching for frequently rendered diagrams
- Enable syntax validation only when needed
- Use appropriate timeouts for external services
- Consider diagram complexity for performance

### Monitoring
```python
from mermaid_render.cache import PerformanceMonitor

monitor = PerformanceMonitor()
with monitor.measure("render_time"):
    result = renderer.render(diagram)

stats = monitor.get_stats()
```

## See Also

- [User Guide](../guides/index.md) - Comprehensive usage examples
- [Examples](../examples/index.md) - Code examples and tutorials
- [Contributing](../contributing/index.md) - Development guidelines
