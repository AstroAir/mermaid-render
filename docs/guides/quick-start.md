# Quick Start Guide

Get up and running with Mermaid Render in just a few minutes!

## Installation

### Basic Installation

```bash
pip install diagramaid
```

### With Optional Features

```bash
# Install with all features
pip install diagramaid[cache,interactive,ai,collaboration,docs]

# Or install specific features
pip install diagramaid[cache,interactive]
```

### Development Installation

```bash
git clone https://github.com/diagramaid/diagramaid.git
cd diagramaid
pip install -e ".[dev]"
```

## Your First Diagram

Let's create a simple flowchart:

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
renderer.save(flowchart, "my_first_diagram.png", format="png")

print("Diagram created successfully!")
```

## Quick Rendering

For simple use cases, use the `quick_render` function:

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

# Render to SVG with dark theme
svg_content = quick_render(diagram_code, format="svg", theme="dark")

# Save to file
quick_render(diagram_code, output_path="decision_flow.png", format="png")
```

## Common Diagram Types

### Sequence Diagram

```python
from diagramaid import SequenceDiagram

sequence = SequenceDiagram(title="User Login")
sequence.add_participant("user", "User")
sequence.add_participant("app", "Application")
sequence.add_participant("db", "Database")

sequence.add_message("user", "app", "Login request")
sequence.add_message("app", "db", "Validate credentials")
sequence.add_message("db", "app", "User data", message_type="return")
sequence.add_message("app", "user", "Login success", message_type="return")

renderer = MermaidRenderer()
renderer.save(sequence, "login_sequence.svg")
```

### Class Diagram

```python
from diagramaid import ClassDiagram
from diagramaid.models.class_diagram import ClassMethod, ClassAttribute

class_diagram = ClassDiagram()

# Add a class
animal = class_diagram.add_class("Animal", is_abstract=True)
animal.add_attribute(ClassAttribute("name", "String", "protected"))
animal.add_method(ClassMethod("move", "public", "void", is_abstract=True))

# Add another class
dog = class_diagram.add_class("Dog")
dog.add_method(ClassMethod("bark", "public", "void"))

# Add inheritance relationship
class_diagram.add_relationship("Dog", "Animal", "inheritance")

renderer = MermaidRenderer()
renderer.save(class_diagram, "animal_hierarchy.svg")
```

## Configuration

### Basic Configuration

```python
from diagramaid import MermaidRenderer, MermaidConfig

# Create custom configuration
config = MermaidConfig(
    timeout=45,
    default_theme="dark",
    validate_syntax=True
)

renderer = MermaidRenderer(config=config)
```

### Environment Variables

```bash
export MERMAID_DEFAULT_THEME="forest"
export MERMAID_TIMEOUT=60
export MERMAID_CACHE_ENABLED=true
```

### Configuration File

```python
from diagramaid.config import ConfigManager

config_manager = ConfigManager(config_file="mermaid_config.json")
config_manager.set("default_theme", "neutral")
config_manager.set("timeout", 30)

renderer = MermaidRenderer(config=config_manager.get_config())
```

## Themes

### Built-in Themes

```python
from diagramaid import MermaidRenderer

# Available themes: default, dark, forest, neutral
renderer = MermaidRenderer(theme="dark")
result = renderer.render(diagram, format="svg")
```

### Custom Themes

```python
from diagramaid import MermaidTheme, MermaidRenderer

# Create custom theme
custom_theme = MermaidTheme(
    name="corporate",
    primaryColor="#2c3e50",
    primaryTextColor="#ffffff",
    lineColor="#34495e"
)

renderer = MermaidRenderer()
renderer.set_theme(custom_theme)
```

## Validation

Always validate your diagrams:

```python
from diagramaid.utils import validate_mermaid_syntax

diagram_code = """
flowchart TD
    A[Start] --> B[End]
"""

result = validate_mermaid_syntax(diagram_code)
if result.is_valid:
    print("✅ Diagram is valid!")
    # Proceed with rendering
else:
    print("❌ Validation errors:")
    for error in result.errors:
        print(f"  - {error}")
```

## Error Handling

```python
from diagramaid.exceptions import ValidationError, RenderingError

try:
    result = renderer.render(diagram, format="svg")
except ValidationError as e:
    print(f"Invalid diagram: {e}")
except RenderingError as e:
    print(f"Rendering failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Output Formats

Mermaid Render supports multiple output formats:

```python
# SVG (vector graphics)
svg_content = renderer.render(diagram, format="svg")

# PNG (raster graphics)
png_data = renderer.render(diagram, format="png")

# PDF (for documents)
pdf_data = renderer.render(diagram, format="pdf")
```

## Batch Operations

### Export Multiple Formats

```python
from diagramaid.utils import export_multiple_formats

# Export to multiple formats at once
export_multiple_formats(
    diagram,
    "output/my_diagram",
    ["svg", "png", "pdf"]
)
```

### Batch Export

```python
from diagramaid.utils import batch_export

diagrams = {
    "flowchart": my_flowchart,
    "sequence": my_sequence,
    "class": my_class_diagram
}

batch_export(diagrams, "output/", format="png", theme="forest")
```

## Next Steps

Now that you've created your first diagrams, explore more advanced features:

1. **[Diagram Types](diagrams/)** - Learn about all supported diagram types
2. **[Themes](advanced/themes.md)** - Customize diagram appearance
3. **[Templates](advanced/templates.md)** - Use pre-built diagram templates
4. **[Caching](advanced/caching.md)** - Improve performance with caching
5. **[Interactive Features](advanced/interactive.md)** - Build interactive diagram tools
6. **[AI Integration](advanced/ai.md)** - Generate diagrams from natural language

## Common Patterns

### Web Application Integration

```python
from flask import Flask, request, jsonify
from diagramaid import quick_render

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render_diagram():
    diagram_code = request.json.get('diagram')
    format = request.json.get('format', 'svg')

    try:
        result = quick_render(diagram_code, format=format)
        return jsonify({'success': True, 'content': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

### Documentation Generation

```python
def generate_architecture_docs(components):
    """Generate architecture diagrams for documentation."""
    flowchart = FlowchartDiagram(title="System Architecture")

    for component in components:
        flowchart.add_node(component.id, component.name)

    for connection in get_connections(components):
        flowchart.add_edge(connection.from_id, connection.to_id)

    renderer = MermaidRenderer(theme="neutral")
    renderer.save(flowchart, "docs/architecture.svg")
```

## Tips for Success

1. **Start Simple**: Begin with basic diagrams and gradually add complexity
2. **Validate Early**: Always validate diagrams before rendering
3. **Use Themes**: Consistent theming improves visual appeal
4. **Handle Errors**: Implement proper error handling for production use
5. **Cache Results**: Use caching for frequently rendered diagrams
6. **Test Thoroughly**: Test with different diagram sizes and complexity

## Getting Help

- 📖 [Full Documentation](../index.md)
- 🔧 [API Reference](../api/index.md)
- 💡 [Examples](../examples/index.md)
- 🐛 [Report Issues](https://github.com/diagramaid/diagramaid/issues)
- 💬 [Discussions](https://github.com/diagramaid/diagramaid/discussions)

Happy diagramming! 🎉
