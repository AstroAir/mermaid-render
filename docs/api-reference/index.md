# API Reference

Complete API documentation for Mermaid Render. This reference covers all classes, methods, and functions available in the library.

## Overview

Mermaid Render is organized into several key modules:

- **[Core](core.md)** - Main classes for rendering and configuration
- **[Models](models.md)** - Diagram model classes for all diagram types
- **[Renderers](renderers.md)** - Backend rendering engines
- **[Utilities](utilities.md)** - Helper functions and utilities
- **[Validators](validators.md)** - Validation and error checking
- **[Configuration](configuration.md)** - Configuration and theme management
- **[Exceptions](exceptions.md)** - Exception classes and error handling

## Quick Reference

### Core Classes

| Class                                        | Description                 |
| -------------------------------------------- | --------------------------- |
| [`MermaidRenderer`](core.md#mermaidrenderer) | Main rendering engine       |
| [`MermaidDiagram`](core.md#mermaiddiagram)   | Base class for all diagrams |
| [`MermaidConfig`](core.md#mermaidconfig)     | Configuration management    |
| [`MermaidTheme`](core.md#mermaidtheme)       | Theme configuration         |

### Diagram Models

| Class                                                | Description                     |
| ---------------------------------------------------- | ------------------------------- |
| [`FlowchartDiagram`](models.md#flowchartdiagram)     | Flowcharts and process diagrams |
| [`SequenceDiagram`](models.md#sequencediagram)       | Sequence diagrams               |
| [`ClassDiagram`](models.md#classdiagram)             | UML class diagrams              |
| [`StateDiagram`](models.md#statediagram)             | State machine diagrams          |
| [`ERDiagram`](models.md#erdiagram)                   | Entity-relationship diagrams    |
| [`UserJourneyDiagram`](models.md#userjourneydiagram) | User journey maps               |
| [`GanttDiagram`](models.md#ganttdiagram)             | Project timelines               |
| [`PieChartDiagram`](models.md#piechartdiagram)       | Pie charts                      |
| [`GitGraphDiagram`](models.md#gitgraphdiagram)       | Git branching diagrams          |
| [`MindmapDiagram`](models.md#mindmapdiagram)         | Mind maps                       |

### Utility Functions

| Function                                                          | Description              |
| ----------------------------------------------------------------- | ------------------------ |
| [`quick_render`](utilities.md#quick_render)                       | Quick diagram rendering  |
| [`validate_mermaid_syntax`](utilities.md#validate_mermaid_syntax) | Syntax validation        |
| [`export_to_file`](utilities.md#export_to_file)                   | Export diagrams to files |
| [`get_supported_formats`](utilities.md#get_supported_formats)     | List supported formats   |
| [`get_available_themes`](utilities.md#get_available_themes)       | List available themes    |

## Usage Patterns

### Basic Rendering

```python
from mermaid_render import MermaidRenderer, FlowchartDiagram

# Create diagram
diagram = FlowchartDiagram()
diagram.add_node("A", "Start")
diagram.add_node("B", "End")
diagram.add_edge("A", "B")

# Render
renderer = MermaidRenderer()
svg_content = renderer.render(diagram, format="svg")
```

### Configuration

```python
from mermaid_render import MermaidConfig, MermaidRenderer

# Configure
config = MermaidConfig(
    timeout=60,
    default_theme="dark",
    validate_syntax=True
)

# Use configuration
renderer = MermaidRenderer(config=config)
```

### Error Handling

```python
from mermaid_render.exceptions import ValidationError, RenderingError

try:
    result = renderer.render(diagram)
except ValidationError as e:
    print(f"Validation error: {e}")
except RenderingError as e:
    print(f"Rendering error: {e}")
```

## Type Hints

Mermaid Render is fully typed with comprehensive type hints:

```python
from typing import Optional, Dict, Any
from mermaid_render import MermaidRenderer, MermaidDiagram

def render_diagram(
    diagram: MermaidDiagram,
    format: str = "svg",
    theme: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> str:
    renderer = MermaidRenderer(theme=theme, config=config)
    return renderer.render(diagram, format=format)
```

## Module Structure

```
mermaid_render/
├── __init__.py          # Main exports
├── core.py              # Core classes
├── models/              # Diagram models
│   ├── __init__.py
│   ├── flowchart.py
│   ├── sequence.py
│   ├── class_diagram.py
│   └── ...
├── renderers/           # Rendering backends
│   ├── __init__.py
│   ├── svg_renderer.py
│   ├── png_renderer.py
│   └── pdf_renderer.py
├── utils/               # Utilities
│   ├── __init__.py
│   ├── validation.py
│   ├── export.py
│   └── helpers.py
├── validators/          # Validation
├── config/              # Configuration
├── exceptions.py        # Exceptions
└── ...
```

## API Stability

Mermaid Render follows semantic versioning:

- **Major versions** (1.0.0 → 2.0.0): Breaking changes
- **Minor versions** (1.0.0 → 1.1.0): New features, backward compatible
- **Patch versions** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Stability Guarantees

- ✅ **Public API**: Stable across minor versions
- ✅ **Core Classes**: Stable interfaces
- ✅ **Diagram Models**: Stable public methods
- ⚠️ **Internal APIs**: May change without notice
- ⚠️ **Experimental Features**: Marked as such in documentation

## Contributing to Documentation

Found an error or want to improve the documentation?

1. Check the [source code](https://github.com/mermaid-render/mermaid-render) for the latest API
2. Submit issues for documentation bugs
3. Contribute improvements via pull requests

## Navigation

Use the navigation menu to explore specific modules:

- **[Core](core.md)** - Start here for main classes
- **[Models](models.md)** - Diagram-specific APIs
- **[Utilities](utilities.md)** - Helper functions
- **[Examples](../examples/)** - Practical usage examples

---

_This documentation is automatically generated from the source code docstrings to ensure accuracy and completeness._
