# Quick Start

Get up and running with Mermaid Render in just a few minutes! This guide will walk you through creating your first diagram.

## Your First Diagram

Let's create a simple flowchart using the object-oriented API:

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
renderer.save(flowchart, "my_first_diagram.png", format="png")

print("✅ Diagram created successfully!")
```

## Quick Rendering with Raw Mermaid

If you prefer working with raw Mermaid syntax:

```python
from mermaid_render import quick_render

# Write your diagram in Mermaid syntax
diagram_code = """
flowchart TD
    A[User Login] --> B{Valid Credentials?}
    B -->|Yes| C[Dashboard]
    B -->|No| D[Error Message]
    D --> A
"""

# Render to SVG with dark theme
svg_content = quick_render(diagram_code, format="svg", theme="dark")

# Save to file
quick_render(diagram_code, output_path="decision_flow.png", format="png")
```

## Common Diagram Types

### Sequence Diagram

```python
from mermaid_render import SequenceDiagram

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
from mermaid_render import ClassDiagram
from mermaid_render.models.class_diagram import ClassMethod, ClassAttribute

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
renderer.save(class_diagram, "class_hierarchy.svg")
```

## Output Formats

Mermaid Render supports multiple output formats:

```python
from mermaid_render import MermaidRenderer, FlowchartDiagram

flowchart = FlowchartDiagram()
flowchart.add_node("A", "Start")
flowchart.add_node("B", "End")
flowchart.add_edge("A", "B")

renderer = MermaidRenderer()

# SVG (vector format, best for web)
renderer.save(flowchart, "diagram.svg", format="svg")

# PNG (raster format, good for documents)
renderer.save(flowchart, "diagram.png", format="png")

# PDF (vector format, best for printing)
renderer.save(flowchart, "diagram.pdf", format="pdf")
```

## Themes

Apply different themes to your diagrams:

```python
from mermaid_render import MermaidRenderer

renderer = MermaidRenderer()

# Built-in themes
themes = ["default", "dark", "forest", "neutral"]

for theme in themes:
    renderer.save(flowchart, f"diagram_{theme}.svg", theme=theme)
```

## Validation

Mermaid Render includes built-in validation:

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

## Configuration

Customize the rendering behavior:

```python
from mermaid_render import MermaidConfig, MermaidRenderer

config = MermaidConfig(
    timeout=60,              # Increase timeout for complex diagrams
    default_theme="dark",    # Set default theme
    validate_syntax=True,    # Enable validation
    cache_enabled=True       # Enable caching for performance
)

renderer = MermaidRenderer(config=config)
```

## Error Handling

Handle errors gracefully:

```python
from mermaid_render import MermaidRenderer
from mermaid_render.exceptions import ValidationError, RenderingError

try:
    renderer = MermaidRenderer()
    result = renderer.render(diagram, format="svg")
except ValidationError as e:
    print(f"Invalid diagram: {e}")
except RenderingError as e:
    print(f"Rendering failed: {e}")
```

## Next Steps

Now that you've created your first diagrams, explore:

- **[Basic Usage](basic-usage.md)** - Learn fundamental concepts and patterns
- **[User Guide](../user-guide/)** - Comprehensive tutorials for all diagram types
- **[Examples](../examples/)** - Real-world usage examples
- **[API Reference](../api-reference/)** - Complete API documentation

## Tips for Success

1. **Start Simple**: Begin with basic diagrams and gradually add complexity
2. **Use Validation**: Always validate your diagrams to catch errors early
3. **Choose the Right Format**: SVG for web, PNG for documents, PDF for printing
4. **Leverage Themes**: Use consistent themes across your diagrams
5. **Handle Errors**: Implement proper error handling in production code

Happy diagramming! 🎨
