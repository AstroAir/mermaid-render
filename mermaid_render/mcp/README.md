# Enhanced MCP Server for Mermaid Render

This directory contains the comprehensive Model Context Protocol (MCP) server implementation for mermaid-render, featuring AI-powered tools, resources, and prompts.

## Overview

The enhanced MCP server exposes the full mermaid-render functionality through the Model Context Protocol, allowing AI assistants and other MCP clients to generate, validate, analyze, and manipulate Mermaid diagrams with advanced AI capabilities.

## Features

### Core Functionality

- **Diagram Rendering**: Render Mermaid diagrams to various formats (SVG, PNG, PDF)
- **Diagram Validation**: Validate Mermaid diagram syntax and structure
- **Theme Management**: List and apply different themes to diagrams

### AI-Powered Features

- **AI Diagram Generation**: Generate diagrams from natural language descriptions
- **Diagram Analysis**: Analyze diagram quality, complexity, and best practices
- **Diagram Optimization**: Optimize diagrams for better readability and structure
- **Smart Suggestions**: Get AI-powered suggestions for diagram improvements

### Template System

- **Template-Based Creation**: Create diagrams from predefined templates
- **Parameter Validation**: Validate template parameters for consistency

### MCP Resources

- **Theme Information**: Access detailed theme specifications and colors
- **Configuration Schema**: Get JSON schema for configuration validation
- **Documentation**: Access comprehensive diagram type documentation
- **Examples**: Browse example diagrams for each diagram type

### MCP Prompts

- **Generation Prompts**: Reusable prompts for diagram generation
- **Analysis Prompts**: Prompts for diagram quality analysis
- **Optimization Prompts**: Prompts for diagram improvement suggestions

## Installation

1. Install FastMCP (required for MCP functionality):

```bash
pip install fastmcp>=2.0.0
```

2. Install optional AI features:

```bash
pip install mermaid-render[ai]
```

3. Install optional template features:

```bash
pip install mermaid-render[templates]
```

## Usage

### Command Line

Start the enhanced MCP server:

```bash
# Using stdio transport (default)
mermaid-render-mcp

# Using SSE transport
mermaid-render-mcp --transport sse --port 8080

# Using WebSocket transport
mermaid-render-mcp --transport websocket --host 0.0.0.0 --port 9000
```

#### Programmatic Usage

```python
from mermaid_render.mcp import create_mcp_server
import asyncio

async def main():
    # Create MCP server
    mcp = create_mcp_server(
        name="mermaid-render",
        version="1.0.0",
        description="Mermaid diagram generation and validation"
    )

    # Run with stdio transport
    await mcp.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using MCP Tools Directly

```python
from mermaid_render.mcp.tools import render_diagram, validate_diagram, list_themes

# Render a diagram
result = render_diagram(
    diagram_code="""
    flowchart TD
        A[Start] --> B[Process]
        B --> C[End]
    """,
    output_format="svg",
    theme="dark"
)

if result["success"]:
    print(f"Rendered {result['format']} diagram")
    print(f"Data length: {len(result['data'])}")
else:
    print(f"Error: {result['error']}")

# Validate diagram syntax
result = validate_diagram("""
    sequenceDiagram
        Alice->>Bob: Hello!
        Bob-->>Alice: Hi there!
""")

print(f"Valid: {result['valid']}")
if result['errors']:
    print(f"Errors: {result['errors']}")

# List available themes
themes = list_themes()
print(f"Available themes: {list(themes['themes'].keys())}")
```

## Configuration

The MCP server can be configured through command-line arguments:

- `--transport`: Transport type (stdio, sse, websocket)
- `--host`: Host address for network transports
- `--port`: Port number for network transports
- `--name`: Server name
- `--version`: Server version
- `--description`: Server description
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Error Handling

All MCP tools return a consistent response format:

```python
{
    "success": bool,           # Whether the operation succeeded
    "error": str,             # Error message (if success=False)
    "error_type": str,        # Error type (if success=False)
    # ... tool-specific data (if success=True)
}
```

## Development

### Testing

To test the MCP tools without a full server setup:

```python
# Test individual tools
from mermaid_render.mcp.tools import render_diagram

result = render_diagram("graph TD; A-->B", output_format="svg")
assert result["success"] is True
```

### Adding New Tools

1. Implement the tool function in `tools.py`
2. Add parameter validation using Pydantic models
3. Register the tool in `register_all_tools()`
4. Add comprehensive error handling
5. Update documentation

## Troubleshooting

### FastMCP Not Found

```
ImportError: FastMCP is required for MCP server functionality
```

Install FastMCP: `pip install fastmcp>=2.0.0`

### Rendering Errors

Check that the underlying mermaid-render dependencies are properly installed and configured.

### Network Transport Issues

Ensure the specified host and port are available and not blocked by firewalls.
