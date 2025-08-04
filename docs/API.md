# Mermaid Render API Documentation

## Core API

### MermaidRenderer

The main class for rendering Mermaid diagrams to various output formats.

```python
from mermaid_render import MermaidRenderer

renderer = MermaidRenderer(
    theme="default",           # Theme name or MermaidTheme object
    format="svg",             # Output format: svg, png, pdf
    config=None,              # MermaidConfig object
    cache_enabled=True        # Enable result caching
)
```

#### Methods

##### `render(diagram, **kwargs) -> str`

Renders a diagram to a string.

**Parameters:**
- `diagram`: Diagram object or raw Mermaid code string
- `**kwargs`: Override renderer settings (theme, format, width, height, etc.)

**Returns:** Rendered diagram as string

**Example:**
```python
svg_content = renderer.render(flowchart, theme="dark", format="svg")
```

##### `save(diagram, filepath, **kwargs) -> None`

Renders and saves a diagram to a file.

**Parameters:**
- `diagram`: Diagram object or raw Mermaid code string
- `filepath`: Output file path
- `**kwargs`: Override renderer settings

**Example:**
```python
renderer.save(sequence_diagram, "output.png", format="png", width=1200)
```

##### `render_batch(diagrams, **kwargs) -> List[str]`

Renders multiple diagrams efficiently.

**Parameters:**
- `diagrams`: List of diagram objects or Mermaid code strings
- `**kwargs`: Common settings for all diagrams

**Returns:** List of rendered diagram strings

### Quick Rendering Functions

#### `quick_render(mermaid_code, **kwargs) -> str`

Quickly render Mermaid code to string.

```python
from mermaid_render import quick_render

svg = quick_render("""
flowchart TD
    A[Start] --> B[End]
""", theme="dark", format="svg")
```

#### `render_to_file(mermaid_code, filepath, **kwargs) -> None`

Quickly render and save Mermaid code to file.

```python
from mermaid_render import render_to_file

render_to_file(mermaid_code, "diagram.png", format="png", theme="forest")
```

## Diagram Models

### FlowchartDiagram

Create flowchart diagrams programmatically.

```python
from mermaid_render import FlowchartDiagram

flowchart = FlowchartDiagram(direction="TD", title="My Flowchart")
flowchart.add_node("start", "Start", shape="rounded")
flowchart.add_node("process", "Process Data", shape="rect")
flowchart.add_edge("start", "process", "Begin")
```

#### Methods

- `add_node(id, label, shape="rect", style=None)`
- `add_edge(from_id, to_id, label=None, style=None)`
- `add_subgraph(id, title, nodes=None)`
- `set_direction(direction)` - TD, LR, BT, RL

### SequenceDiagram

Create sequence diagrams for interaction flows.

```python
from mermaid_render import SequenceDiagram

sequence = SequenceDiagram(title="User Login")
sequence.add_participant("user", "User")
sequence.add_participant("app", "Application")
sequence.add_message("user", "app", "Login request")
sequence.add_activation("app")
sequence.add_note("app", "Validate credentials", position="right")
```

#### Methods

- `add_participant(id, name, type="participant")`
- `add_message(from_id, to_id, message, type="arrow")`
- `add_activation(participant_id)`
- `add_deactivation(participant_id)`
- `add_note(participant_id, text, position="right")`
- `add_loop(condition, messages)`

### ClassDiagram

Create UML class diagrams.

```python
from mermaid_render import ClassDiagram
from mermaid_render.models.class_diagram import ClassMethod, ClassAttribute

class_diagram = ClassDiagram()
animal = class_diagram.add_class("Animal", is_abstract=True)
animal.add_attribute(ClassAttribute("name", "String", "protected"))
animal.add_method(ClassMethod("move", "public", "void", is_abstract=True))
```

#### Methods

- `add_class(name, is_abstract=False, stereotype=None)`
- `add_relationship(from_class, to_class, type, label=None)`
- `add_interface(name)`
- `add_enum(name, values)`

### Other Diagram Types

- `StateDiagram` - State machines and transitions
- `ERDiagram` - Entity-relationship diagrams
- `GanttDiagram` - Project timelines
- `PieChartDiagram` - Data visualization
- `UserJourneyDiagram` - User experience flows
- `GitGraphDiagram` - Git branching visualization
- `MindmapDiagram` - Hierarchical information

## Configuration

### MermaidConfig

Global configuration for rendering behavior.

```python
from mermaid_render.config import MermaidConfig

config = MermaidConfig(
    theme="default",
    background_color="white",
    width=800,
    height=600,
    scale=1.0,
    timeout=30,
    cache_enabled=True,
    output_directory="./diagrams"
)
```

### ThemeManager

Manage built-in and custom themes.

```python
from mermaid_render.config import ThemeManager

theme_manager = ThemeManager()

# List available themes
themes = theme_manager.list_themes()

# Get theme details
theme = theme_manager.get_theme("dark")

# Create custom theme
custom_theme = theme_manager.create_theme(
    "my_theme",
    primaryColor="#ff6b6b",
    primaryTextColor="#ffffff",
    lineColor="#4ecdc4"
)
```

## Validation and Error Handling

### Syntax Validation

```python
from mermaid_render.utils import validate_mermaid_syntax

try:
    is_valid, errors = validate_mermaid_syntax(mermaid_code)
    if not is_valid:
        print(f"Validation errors: {errors}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Exception Types

- `MermaidRenderError` - Base exception class
- `ValidationError` - Diagram syntax validation errors
- `RenderingError` - Rendering process errors
- `ConfigurationError` - Configuration-related errors
- `ThemeError` - Theme-related errors

## Advanced Features

### Caching

```python
from mermaid_render.cache import CacheManager

cache_manager = CacheManager(backend="memory")  # or "redis", "file"
renderer = MermaidRenderer(cache_manager=cache_manager)
```

### AI-Powered Features

```python
from mermaid_render.ai import DiagramGenerator, NLProcessor

# Generate diagrams from natural language
generator = DiagramGenerator()
diagram = generator.from_description("Create a login flow diagram")

# Process natural language to Mermaid syntax
processor = NLProcessor()
mermaid_code = processor.text_to_mermaid("User logs in, system validates, returns token")
```

### Interactive Features

```python
from mermaid_render.interactive import InteractiveServer

# Start interactive web interface
server = InteractiveServer(port=8080)
server.start()  # Access at http://localhost:8080
```

## Performance Optimization

### Batch Rendering

```python
diagrams = [flowchart1, flowchart2, sequence1]
results = renderer.render_batch(diagrams, format="svg", theme="dark")
```

### Async Rendering

```python
import asyncio
from mermaid_render import AsyncMermaidRenderer

async def render_async():
    renderer = AsyncMermaidRenderer()
    result = await renderer.render_async(diagram)
    return result

result = asyncio.run(render_async())
```

### Memory Management

```python
# Clear cache periodically
renderer.clear_cache()

# Use context manager for automatic cleanup
with MermaidRenderer() as renderer:
    result = renderer.render(diagram)
```
