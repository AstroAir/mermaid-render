# MCP Configuration Files

This directory contains configuration files for integrating diagramaid MCP server with various AI assistants and IDE extensions.

## Quick Start

### Prerequisites

1. Install diagramaid with MCP support:
```bash
pip install diagramaid[all]
# or
pip install diagramaid fastmcp
```

2. Verify installation:
```bash
diagramaid-mcp --help
```

## Configuration for Different Clients

### Claude Desktop

1. Copy the configuration to Claude Desktop's config directory:

**Windows:**
```powershell
copy claude_desktop_config.json "$env:APPDATA\Claude\claude_desktop_config.json"
```

**macOS:**
```bash
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Linux:**
```bash
cp claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json
```

2. Restart Claude Desktop

### Cursor IDE

1. Open Cursor Settings
2. Navigate to "MCP Servers" section
3. Add the configuration from `cursor_config.json`
4. Restart Cursor

### Windsurf IDE

1. Open Windsurf Settings
2. Navigate to "MCP" section
3. Add the configuration from `windsurf_config.json`
4. Restart Windsurf

### Generic MCP Client

Use `mcp.json` as a reference for configuring any MCP-compatible client.

## Transport Options

### stdio (Default)
```bash
diagramaid-mcp
```
Best for local integrations with desktop applications.

### SSE (Server-Sent Events)
```bash
diagramaid-mcp --transport sse --host localhost --port 8000
```
Best for web-based integrations.

### WebSocket
```bash
diagramaid-mcp --transport websocket --host localhost --port 9000
```
Best for real-time bidirectional communication.

## Available Tools

| Tool | Description |
|------|-------------|
| `render_diagram` | Render Mermaid diagram to SVG/PNG/PDF |
| `validate_diagram` | Validate diagram syntax |
| `list_themes` | List available themes |
| `generate_diagram_from_text` | AI-powered diagram generation |
| `optimize_diagram` | Optimize diagram for readability |
| `analyze_diagram` | Analyze diagram metrics |
| `get_diagram_suggestions` | Get improvement suggestions |
| `create_from_template` | Create from template |
| `list_diagram_types` | List supported diagram types |
| `get_diagram_examples` | Get example code |
| `convert_diagram_format` | Convert between formats |
| `merge_diagrams` | Merge multiple diagrams |
| `extract_diagram_elements` | Extract nodes/edges |
| `compare_diagrams` | Compare two diagrams |
| `export_to_markdown` | Export with documentation |

## Available Prompts

| Prompt | Description |
|--------|-------------|
| `generate_flowchart` | Generate flowchart from description |
| `generate_sequence` | Generate sequence diagram |
| `generate_class_diagram` | Generate class diagram |
| `generate_er_diagram` | Generate ER diagram |
| `generate_state_diagram` | Generate state diagram |
| `generate_gantt_chart` | Generate Gantt chart |
| `generate_mindmap` | Generate mind map |
| `analyze_diagram_quality` | Analyze diagram quality |
| `explain_diagram` | Explain diagram content |
| `refactor_diagram` | Refactor diagram structure |

## Available Resources

| URI | Description |
|-----|-------------|
| `mermaid://themes` | List of themes |
| `mermaid://templates` | List of templates |
| `mermaid://docs/diagram-types` | Diagram type documentation |
| `mermaid://syntax/{type}` | Syntax reference |
| `mermaid://best-practices` | Best practices guide |
| `mermaid://capabilities` | Server capabilities |

## Troubleshooting

### Server not starting
```bash
# Check if diagramaid-mcp is in PATH
which diagramaid-mcp  # Unix
where diagramaid-mcp  # Windows

# Run with debug logging
diagramaid-mcp --log-level DEBUG
```

### Connection issues
- Ensure no firewall blocking the port (for SSE/WebSocket)
- Check if port is already in use
- Verify Python environment is activated

### Missing features
```bash
# Install all optional dependencies
pip install diagramaid[all]
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `diagramaid_LOG_LEVEL` | Logging level | INFO |
| `diagramaid_CACHE_DIR` | Cache directory | ~/.diagramaid_cache |
| `OPENAI_API_KEY` | OpenAI API key for AI features | - |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI features | - |

## Support

- GitHub Issues: https://github.com/AstroAir/diagramaid/issues
- Documentation: https://diagramaid.readthedocs.io
