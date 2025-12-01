# Basic Usage

This guide covers the fundamental concepts and patterns you'll use when working with Mermaid Render.

## Core Concepts

### Diagram Objects vs Raw Syntax

Mermaid Render supports two approaches:

1. **Object-Oriented API**: Create diagrams using Python classes
2. **Raw Mermaid Syntax**: Work directly with Mermaid code strings

```python
# Object-oriented approach
from diagramaid import FlowchartDiagram

flowchart = FlowchartDiagram()
flowchart.add_node("A", "Start")
flowchart.add_node("B", "End")
flowchart.add_edge("A", "B")

# Raw syntax approach
diagram_code = """
flowchart TD
    A[Start] --> B[End]
"""
```

### The Rendering Pipeline

All diagrams go through the same rendering pipeline:

1. **Creation**: Build diagram using API or raw syntax
2. **Validation**: Check for syntax errors and structural issues
3. **Rendering**: Convert to target format (SVG, PNG, PDF)
4. **Output**: Save to file or return as string/bytes

```python
from diagramaid import MermaidRenderer, FlowchartDiagram

# 1. Creation
diagram = FlowchartDiagram()
diagram.add_node("A", "Start")

# 2. Validation (automatic)
# 3. Rendering
renderer = MermaidRenderer()
svg_content = renderer.render(diagram, format="svg")

# 4. Output
renderer.save(diagram, "output.png", format="png")
```

## Working with Diagrams

### Creating Diagram Objects

Each diagram type has its own class:

```python
from diagramaid import (
    FlowchartDiagram,
    SequenceDiagram,
    ClassDiagram,
    StateDiagram
)

# Create different diagram types
flowchart = FlowchartDiagram(direction="TD", title="My Process")
sequence = SequenceDiagram(title="API Flow", autonumber=True)
class_diagram = ClassDiagram(title="System Architecture")
state = StateDiagram(title="State Machine")
```

### Building Diagrams Programmatically

Use the fluent API to build diagrams step by step:

```python
from diagramaid import FlowchartDiagram

# Create and build a flowchart
flowchart = FlowchartDiagram(direction="TD")

# Add nodes with different shapes
flowchart.add_node("start", "Start Process", shape="circle")
flowchart.add_node("input", "Get User Input", shape="rectangle")
flowchart.add_node("validate", "Valid Input?", shape="diamond")
flowchart.add_node("process", "Process Data", shape="rectangle")
flowchart.add_node("error", "Show Error", shape="rectangle")
flowchart.add_node("end", "End", shape="circle")

# Connect nodes with edges
flowchart.add_edge("start", "input")
flowchart.add_edge("input", "validate")
flowchart.add_edge("validate", "process", label="Yes")
flowchart.add_edge("validate", "error", label="No")
flowchart.add_edge("process", "end")
flowchart.add_edge("error", "input", label="Retry")
```

### Converting to Mermaid Syntax

All diagram objects can generate Mermaid syntax:

```python
# Get the Mermaid code
mermaid_code = flowchart.to_mermaid()
print(mermaid_code)

# Output:
# flowchart TD
#     start([Start Process])
#     input[Get User Input]
#     validate{Valid Input?}
#     ...
```

## Rendering and Output

### The MermaidRenderer Class

The `MermaidRenderer` is your main interface for converting diagrams to output formats:

```python
from diagramaid import MermaidRenderer, MermaidConfig

# Basic renderer
renderer = MermaidRenderer()

# Renderer with custom configuration
config = MermaidConfig(timeout=60, validate_syntax=True)
renderer = MermaidRenderer(config=config, theme="dark")
```

### Output Formats

Support for multiple output formats:

```python
# Render to different formats
svg_content = renderer.render(diagram, format="svg")
png_bytes = renderer.render(diagram, format="png")
pdf_bytes = renderer.render(diagram, format="pdf")

# Save directly to files
renderer.save(diagram, "diagram.svg", format="svg")
renderer.save(diagram, "diagram.png", format="png", width=800, height=600)
renderer.save(diagram, "diagram.pdf", format="pdf")
```

### Quick Rendering Functions

For simple use cases, use the convenience functions:

```python
from diagramaid import quick_render, render_to_file

# Quick render to string
svg_content = quick_render(diagram_code, format="svg", theme="dark")

# Quick render to file
render_to_file(diagram_code, "output.png", format="png", theme="forest")
```

## Configuration and Themes

### Global Configuration

Configure default behavior:

```python
from diagramaid import MermaidConfig

config = MermaidConfig(
    timeout=30,                    # Request timeout in seconds
    default_theme="dark",          # Default theme
    validate_syntax=True,          # Enable validation
    cache_enabled=True,            # Enable caching
    server_url="https://mermaid.ink"  # Rendering server
)
```

### Theme Management

Apply themes to your diagrams:

```python
from diagramaid import MermaidRenderer

renderer = MermaidRenderer()

# Built-in themes
built_in_themes = ["default", "dark", "forest", "neutral", "base"]

# Apply theme during rendering
svg_content = renderer.render(diagram, theme="dark")

# Set default theme
renderer = MermaidRenderer(theme="forest")
```

### Custom Themes

Create custom themes:

```python
from diagramaid import MermaidTheme

custom_theme = MermaidTheme(
    name="corporate",
    primaryColor="#2c3e50",
    primaryTextColor="#ffffff",
    lineColor="#34495e",
    backgroundColor="#ecf0f1"
)

renderer = MermaidRenderer(theme=custom_theme)
```

## Validation and Error Handling

### Built-in Validation

Mermaid Render validates diagrams automatically:

```python
from diagramaid.utils import validate_mermaid_syntax

# Validate raw Mermaid syntax
result = validate_mermaid_syntax(diagram_code)

if result.is_valid:
    print("✅ Diagram is valid")
else:
    print("❌ Validation errors:")
    for error in result.errors:
        print(f"  - {error}")

    print("⚠️ Warnings:")
    for warning in result.warnings:
        print(f"  - {warning}")
```

### Exception Handling

Handle different types of errors:

```python
from diagramaid.exceptions import (
    ValidationError,
    RenderingError,
    UnsupportedFormatError,
    ConfigurationError
)

try:
    renderer = MermaidRenderer()
    result = renderer.render(diagram, format="svg")

except ValidationError as e:
    print(f"Invalid diagram syntax: {e}")

except RenderingError as e:
    print(f"Rendering failed: {e}")

except UnsupportedFormatError as e:
    print(f"Format not supported: {e}")

except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

### 1. Use Validation Early

Always validate diagrams during development:

```python
# Validate before rendering
if not diagram.validate().is_valid:
    print("Fix diagram errors before rendering")
    return
```

### 2. Handle Errors Gracefully

Implement proper error handling:

```python
def safe_render(diagram, output_path):
    try:
        renderer = MermaidRenderer()
        renderer.save(diagram, output_path)
        return True
    except Exception as e:
        print(f"Failed to render diagram: {e}")
        return False
```

### 3. Use Appropriate Output Formats

Choose the right format for your use case:

- **SVG**: Web pages, scalable graphics
- **PNG**: Documents, presentations, fixed-size images
- **PDF**: Printing, high-quality documents

### 4. Leverage Caching

Enable caching for better performance:

```python
config = MermaidConfig(cache_enabled=True)
renderer = MermaidRenderer(config=config)
```

### 5. Consistent Theming

Use consistent themes across your application:

```python
# Set up a theme manager
from diagramaid.config import ThemeManager

theme_manager = ThemeManager()
theme_manager.set_default_theme("corporate")
```

## Troubleshooting

### Common Issues

#### "Connection timeout" errors

```python
# Increase timeout
config = MermaidConfig(timeout=60)
renderer = MermaidRenderer(config=config)
```

#### "Invalid diagram syntax" errors

```python
# Use validation to debug
result = validate_mermaid_syntax(diagram_code)
for error in result.errors:
    print(f"Error: {error}")
```

#### PDF export not working

```bash
# Install PDF dependencies
pip install diagramaid[pdf]
```

### Performance Tips

1. **Enable caching** for repeated renders
2. **Use SVG format** when possible (fastest)
3. **Validate once** and render multiple times
4. **Batch operations** when rendering multiple diagrams

## Next Steps

Now that you understand the basics:

- Explore the [User Guide](../user-guide/) for detailed tutorials
- Check out [Examples](../examples/) for real-world patterns
- Browse the [API Reference](../api-reference/) for complete documentation
