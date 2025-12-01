# Mermaid Render

[![PyPI version](https://badge.fury.io/py/diagramaid.svg)](https://badge.fury.io/py/diagramaid)
[![Python Support](https://img.shields.io/pypi/pyversions/diagramaid.svg)](https://pypi.org/project/diagramaid/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/AstroAir/diagramaid/workflows/Tests/badge.svg)](https://github.com/AstroAir/diagramaid/actions)
[![Coverage](https://codecov.io/gh/AstroAir/diagramaid/branch/main/graph/badge.svg)](https://codecov.io/gh/AstroAir/diagramaid)

A comprehensive, production-ready Python library for generating Mermaid diagrams with clean APIs, validation, multiple output formats, AI-powered generation, and MCP server integration.

## ✨ Key Features

- **Complete Diagram Support**: All major Mermaid diagram types (flowchart, sequence, class, state, ER, journey, gantt, pie, gitgraph, mindmap, timeline)
- **Multiple Output Formats**: SVG, PNG, PDF with high-quality rendering
- **Plugin-Based Architecture**: Extensible renderer system with automatic fallback
- **Enhanced Validation**: Multi-level validation with detailed error reporting
- **Theme Management**: Built-in themes plus custom theme support
- **Flexible Configuration**: Environment variables, config files, runtime options
- **AI-Powered Generation**: Natural language to diagram conversion with OpenAI, Anthropic, OpenRouter
- **Template System**: Pre-built templates and data-driven diagram generation
- **Interactive Builder**: Web-based visual diagram builder with real-time preview
- **MCP Server**: Model Context Protocol server for AI assistant integration
- **Type Safety**: Full type hints and strict mypy compatibility
- **Rich Documentation**: Comprehensive docs with examples
- **Thoroughly Tested**: 95%+ test coverage with unit and integration tests

## 🚀 Quick Start

### Installation

```bash
pip install diagramaid
```

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
from diagramaid import quick_render

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
| Timeline     | `TimelineDiagram`    | Timeline visualization               |

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
- MCP server for AI assistant integration
- Template system for data-driven diagrams

## 🔌 Advanced Features

### AI-Powered Generation

```python
from diagramaid.ai import generate_from_text

diagram = generate_from_text(
    "Create a flowchart showing the user registration process"
)
```

### Template System

```python
from diagramaid.templates import generate_from_template

diagram = generate_from_template("software_architecture", {
    "title": "My System",
    "services": [{"id": "api", "name": "API Gateway"}],
    "connections": [{"from": "api", "to": "db"}]
})
```

### Interactive Builder

```python
from diagramaid.interactive import start_server

start_server(host="localhost", port=8080)
# Access at http://localhost:8080
```

### MCP Server

```bash
# Start MCP server for AI assistant integration
diagramaid-mcp
```

## 📚 Documentation

- **[Getting Started](getting-started/)** - Installation and quick start guide
- **[User Guide](user-guide/)** - Comprehensive tutorials and examples
- **[API Reference](api-reference/)** - Complete API documentation
- **[Examples](examples/)** - Real-world usage examples
- **[Architecture](architecture/)** - System architecture and design
- **[Development](development/)** - Contributing and development setup

## 🤝 Community & Support

- 📖 **Documentation**: [Full API Documentation](https://diagramaid.readthedocs.io)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AstroAir/diagramaid/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/AstroAir/diagramaid/discussions)
- 📧 **Email**: [astro_air@126.com](mailto:astro_air@126.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/AstroAir/diagramaid/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments

- [Mermaid.js](https://mermaid.js.org/) - The amazing diagramming library
- [mermaid-py](https://github.com/ouhammmourachid/mermaid-py) - Python interface to Mermaid
- [mermaid.ink](https://mermaid.ink/) - Online Mermaid rendering service
- [FastMCP](https://github.com/jlowin/fastmcp) - Model Context Protocol framework

---

Made with ❤️ by Max Qian
