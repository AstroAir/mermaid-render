# MCP Server Module

This module contains the comprehensive Model Context Protocol (MCP) server implementation for mermaid-render, featuring AI-powered tools, resources, and prompts.

## Quick Start

### One-Click Setup

Configuration files for popular AI assistants are available in the `mcp-config/` directory:

- **Claude Desktop**: Copy `mcp-config/claude_desktop_config.json` to your Claude config directory
- **Cursor IDE**: Use `mcp-config/cursor_config.json`
- **Windsurf IDE**: Use `mcp-config/windsurf_config.json`

### Installation

```bash
# Install with all features
pip install mermaid-render[all]

# Or install with specific features
pip install mermaid-render fastmcp
```

### Start the Server

```bash
# Using stdio transport (default, for desktop apps)
mermaid-render-mcp

# Using SSE transport (for web integrations)
mermaid-render-mcp --transport sse --port 8080

# Using WebSocket transport (for real-time apps)
mermaid-render-mcp --transport websocket --port 9000
```

## Features Overview

### Tools (26 total)

#### Core Tools

| Tool | Description |
|------|-------------|
| `render_diagram` | Render Mermaid diagrams to SVG/PNG/PDF |
| `validate_diagram` | Validate diagram syntax and structure |
| `list_themes` | List available themes with details |

#### AI-Powered Tools

| Tool | Description |
|------|-------------|
| `generate_diagram_from_text` | Generate diagrams from natural language |
| `optimize_diagram` | Optimize diagram layout and structure |
| `analyze_diagram` | Analyze diagram quality and complexity |
| `get_diagram_suggestions` | Get AI-powered improvement suggestions |

#### Template Tools

| Tool | Description |
|------|-------------|
| `create_from_template` | Create diagrams from templates |
| `list_available_templates` | List all available templates |
| `get_template_details` | Get detailed template information |
| `create_custom_template` | Create custom templates |

#### Extended Tools

| Tool | Description |
|------|-------------|
| `convert_diagram_format` | Convert between output formats |
| `merge_diagrams` | Merge multiple diagrams into one |
| `extract_diagram_elements` | Extract nodes and edges from diagrams |
| `compare_diagrams` | Compare two diagrams for differences |
| `export_to_markdown` | Export diagram with documentation |
| `transform_diagram_style` | Apply style presets to diagrams |
| `generate_diagram_variants` | Generate layout/style variants |

#### Management Tools

| Tool | Description |
|------|-------------|
| `get_configuration` | Get current configuration |
| `update_configuration` | Update configuration settings |
| `get_system_information` | Get system capabilities |
| `save_diagram_to_file` | Save rendered diagram to file |
| `batch_render_diagrams` | Render multiple diagrams in batch |
| `manage_cache_operations` | Manage cache (stats, clear, cleanup) |
| `list_diagram_types` | List supported diagram types |
| `get_diagram_examples` | Get example code for diagram types |

### Prompts (21 total)

#### Generation Prompts

| Prompt | Description |
|--------|-------------|
| `generate_flowchart` | Generate flowchart from process description |
| `generate_sequence` | Generate sequence diagram from interactions |
| `generate_class_diagram` | Generate class diagram from system description |
| `generate_er_diagram` | Generate ER diagram from database schema |
| `generate_state_diagram` | Generate state diagram from state machine |
| `generate_gantt_chart` | Generate Gantt chart from project plan |
| `generate_mindmap` | Generate mind map from topic |
| `generate_timeline` | Generate timeline from events |
| `generate_pie_chart` | Generate pie chart from data |
| `generate_git_graph` | Generate git graph from workflow |
| `generate_c4_diagram` | Generate C4 architecture diagram |

#### Analysis & Optimization Prompts

| Prompt | Description |
|--------|-------------|
| `analyze_diagram_quality` | Analyze diagram for quality and best practices |
| `suggest_improvements` | Suggest improvements for a diagram |
| `optimize_layout` | Optimize diagram layout |
| `simplify_diagram` | Simplify complex diagrams |
| `refactor_diagram` | Refactor and improve diagram structure |

#### Documentation Prompts

| Prompt | Description |
|--------|-------------|
| `explain_diagram` | Generate explanation of a diagram |
| `create_diagram_documentation` | Create comprehensive documentation |
| `document_architecture` | Create architecture documentation |

#### Transformation Prompts

| Prompt | Description |
|--------|-------------|
| `translate_diagram` | Translate diagram labels to another language |
| `convert_to_diagram` | Convert other formats to Mermaid diagrams |

### Resources (13 total)

| URI | Description |
|-----|-------------|
| `mermaid://themes` | List of all available themes |
| `mermaid://themes/{name}` | Details for specific theme |
| `mermaid://templates` | List of all templates |
| `mermaid://templates/{name}` | Details for specific template |
| `mermaid://config/schema` | Configuration JSON schema |
| `mermaid://config/defaults` | Default configuration values |
| `mermaid://docs/diagram-types` | Diagram type documentation |
| `mermaid://examples/{type}` | Examples for diagram types |
| `mermaid://syntax/{type}` | Syntax reference for diagram types |
| `mermaid://best-practices` | Best practices guide |
| `mermaid://capabilities` | Server capabilities and features |
| `mermaid://changelog` | Version changelog |
| `mermaid://shortcuts` | Quick reference for common patterns |

## Usage Examples

### Programmatic Usage

```python
from mermaid_render.mcp import create_mcp_server
import asyncio

async def main():
    # Create MCP server with all features
    mcp = create_mcp_server(
        name="mermaid-render",
        version="1.0.0"
    )
    
    # Run with stdio transport
    await mcp.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Tools Directly

```python
from mermaid_render.mcp import (
    render_diagram,
    validate_diagram,
    merge_diagrams,
    export_to_markdown
)

# Render a diagram
result = render_diagram(
    diagram_code="flowchart TD\n    A[Start] --> B[End]",
    output_format="svg",
    theme="dark"
)

# Merge multiple diagrams
result = merge_diagrams(
    diagrams=[
        {"code": "flowchart TD\n    A --> B", "name": "Process 1"},
        {"code": "flowchart TD\n    C --> D", "name": "Process 2"}
    ],
    merge_strategy="subgraph"
)

# Export to Markdown
result = export_to_markdown(
    diagram_code="flowchart TD\n    A --> B",
    title="My Diagram",
    description="This diagram shows...",
    include_elements=True
)
```

## Configuration

### Command-Line Options

```bash
mermaid-render-mcp [OPTIONS]

Options:
  --transport [stdio|sse|websocket]  Transport type (default: stdio)
  --host TEXT                        Host address (default: localhost)
  --port INTEGER                     Port number (default: 8000)
  --name TEXT                        Server name (default: mermaid-render)
  --version TEXT                     Server version (default: 1.0.0)
  --log-level [DEBUG|INFO|WARNING|ERROR]  Logging level (default: INFO)
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for AI features |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI features |
| `MERMAID_RENDER_CACHE_DIR` | Cache directory path |
| `MERMAID_RENDER_LOG_LEVEL` | Logging level |

## Response Format

All tools return a consistent response format:

```python
{
    "success": True,           # Operation status
    "data": {...},             # Tool-specific data
    "metadata": {...},         # Additional metadata
    "timestamp": "...",        # ISO timestamp
    "performance": {           # Performance metrics
        "execution_time_ms": 42.5
    }
}
```

Error responses:

```python
{
    "success": False,
    "error": "Error message",
    "error_type": "ValidationError",
    "error_category": "ValidationError",
    "suggestions": ["Suggestion 1", "Suggestion 2"],
    "context": {...}
}
```

## Module Structure

```
mermaid_render/mcp/
├── __init__.py           # Package exports
├── server.py             # MCP server implementation
├── tools.py              # Core tool implementations
├── extended_tools.py     # Extended tool implementations
├── prompts.py            # Core prompt implementations
├── extended_prompts.py   # Extended prompt implementations
├── resources.py          # Core resource implementations
└── extended_resources.py # Extended resource implementations
```

## Troubleshooting

### FastMCP Not Found

```bash
pip install fastmcp>=2.0.0
```

### AI Features Not Available

```bash
pip install mermaid-render[ai]
# Set API keys
export OPENAI_API_KEY=your_key
```

### Template Features Not Available

```bash
pip install mermaid-render[templates]
```

### Debug Mode

```bash
mermaid-render-mcp --log-level DEBUG
```

## Contributing

1. Add new tools in `extended_tools.py`
2. Add new prompts in `extended_prompts.py`
3. Add new resources in `extended_resources.py`
4. Register in respective `register_*` functions
5. Update this documentation
6. Add tests in `tests/integration/test_mcp_server_integration.py`
