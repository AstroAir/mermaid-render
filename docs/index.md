# Mermaid Render

[![PyPI version](https://badge.fury.io/py/mermaid-render.svg)](https://badge.fury.io/py/mermaid-render)
[![Python Support](https://img.shields.io/pypi/pyversions/mermaid-render.svg)](https://pypi.org/project/mermaid-render/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/mermaid-render/mermaid-render/workflows/Tests/badge.svg)](https://github.com/mermaid-render/mermaid-render/actions)
[![Coverage](https://codecov.io/gh/mermaid-render/mermaid-render/branch/main/graph/badge.svg)](https://codecov.io/gh/mermaid-render/mermaid-render)

A comprehensive, production-ready Python library for generating Mermaid diagrams with clean APIs, validation, and multiple output formats.

## ✨ Key Features

- **Complete Diagram Support**: All major Mermaid diagram types (flowchart, sequence, class, state, ER, etc.)
- **Multiple Output Formats**: SVG, PNG, PDF with high-quality rendering
- **Syntax Validation**: Built-in validation with helpful error messages
- **Theme Management**: Built-in themes plus custom theme support
- **Flexible Configuration**: Environment variables, config files, runtime options
- **Type Safety**: Full type hints and mypy compatibility
- **Rich Documentation**: Comprehensive docs with examples
- **Thoroughly Tested**: 95%+ test coverage with unit and integration tests

## 🚀 Quick Start

### Installation

```bash
pip install mermaid-render
```

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
from mermaid_render import quick_render

# Write your diagram in Mermaid syntax
diagram_code = """
flowchart TD
    A[User Login] --> B{Valid Credentials?}
    B -->|Yes| C[Dashboard]
    B -->|No| D[Error Message]
    D --> A
"""

# Render and save
svg_content = quick_render(diagram_code, "login_flow.svg", theme="dark")
print("✅ Diagram saved as login_flow.svg")
```

## 📊 Supported Diagram Types

| Diagram Type | Class                | Description                          |
| ------------ | -------------------- | ------------------------------------ |
| Flowchart    | `FlowchartDiagram`   | Process flows and decision trees     |
| Sequence     | `SequenceDiagram`    | Interaction sequences between actors |
| Class        | `ClassDiagram`       | UML class relationships              |
| State        | `StateDiagram`       | State machines and transitions       |
| ER           | `ERDiagram`          | Entity-relationship diagrams         |
| User Journey | `UserJourneyDiagram` | User experience flows                |
| Gantt        | `GanttDiagram`       | Project timelines                    |
| Pie Chart    | `PieChartDiagram`    | Data visualization                   |
| Git Graph    | `GitGraphDiagram`    | Git branching visualization          |
| Mindmap      | `MindmapDiagram`     | Hierarchical information             |

## 🎯 Why Choose Mermaid Render?

### Production Ready

- Comprehensive error handling and validation
- Extensive test coverage (95%+)
- Type-safe with full mypy support
- Performance optimized with caching

### Developer Friendly

- Clean, intuitive APIs
- Comprehensive documentation with examples
- IDE support with full type hints
- Flexible configuration options

### Feature Rich

- Multiple output formats (SVG, PNG, PDF)
- Built-in and custom themes
- AI-powered diagram generation
- Interactive web interface
- Collaboration features

## 📚 Documentation

- **[Getting Started](getting-started/)** - Installation and quick start guide
- **[User Guide](user-guide/)** - Comprehensive tutorials and examples
- **[API Reference](api-reference/)** - Complete API documentation
- **[Examples](examples/)** - Real-world usage examples
- **[Development](development/)** - Contributing and development setup

## 🤝 Community & Support

- 📖 **Documentation**: [Full API Documentation](https://mermaid-render.readthedocs.io)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/mermaid-render/mermaid-render/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/mermaid-render/mermaid-render/discussions)
- 📧 **Email**: [support@mermaid-render.dev](mailto:support@mermaid-render.dev)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/mermaid-render/mermaid-render/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments

- [Mermaid.js](https://mermaid.js.org/) - The amazing diagramming library
- [mermaid-py](https://github.com/ouhammmourachid/mermaid-py) - Python interface to Mermaid
- [mermaid.ink](https://mermaid.ink/) - Online Mermaid rendering service

---

Made with ❤️ by the Mermaid Render team
