"""
FastMCP server implementation for diagramaid.

This module creates and configures the MCP server that exposes diagramaid
functionality through the Model Context Protocol. It leverages FastMCP's
advanced features including:

- Context-aware tools with logging and progress reporting
- Resource templates for dynamic content
- Prompts for AI-assisted diagram generation and repair
- Comprehensive error handling and validation

The server provides a complete workflow for:
1. Generating Mermaid diagrams from natural language
2. Validating and repairing diagram syntax
3. Rendering diagrams to various formats (SVG, PNG, PDF)
4. AI-powered optimization and suggestions
"""

import argparse
import asyncio
import logging
from typing import Any

try:
    from fastmcp import FastMCP

    _FASTMCP_AVAILABLE = True
except ImportError:
    FastMCP = None
    _FASTMCP_AVAILABLE = False

from .prompts import register_all_prompts, register_extended_prompts
from .resources import register_all_resources, register_extended_resources
from .tools import register_all_tools, register_extended_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server instructions for LLM clients
SERVER_INSTRUCTIONS = """
# Mermaid Render MCP Server

This server provides comprehensive tools for working with Mermaid diagrams.

## Quick Start Workflow

1. **Generate**: Use `generate_diagram_from_text` to create diagrams from descriptions
2. **Validate**: Use `validate_diagram` to check syntax before rendering
3. **Repair**: Use `repair_diagram` for automatic fixing of common issues
4. **Render**: Use `render_diagram` to output SVG, PNG, or PDF

## Auto-Repair Workflow

When a diagram has errors:
1. Call `validate_and_repair` with `auto_repair=true` for one-step fix
2. Or call `get_repair_suggestions` to see what can be fixed
3. For complex issues, use `repair_diagram` with `strategy="ai_assisted"`

## Available Diagram Types

- flowchart: Process flows and decision trees
- sequenceDiagram: Interaction sequences
- classDiagram: UML class diagrams
- stateDiagram: State machines
- erDiagram: Entity-relationship diagrams
- gantt: Project timelines
- pie: Pie charts
- mindmap: Mind maps
- timeline: Historical timelines
- gitgraph: Git branch visualization

## Best Practices

- Always validate before rendering
- Use themes for consistent styling
- Leverage templates for common patterns
- Use the repair workflow for fixing errors
"""


def create_mcp_server(
    name: str = "diagramaid",
    version: str = "1.0.0",
    description: str | None = None,
    include_instructions: bool = True,
) -> Any:
    """
    Create and configure the MCP server for diagramaid.

    This function creates a fully configured FastMCP server with all tools,
    resources, and prompts registered. It leverages FastMCP features including:
    - Server instructions for LLM guidance
    - Tagged tools for organization
    - Resource templates for dynamic content
    - Context-aware tools with logging and progress

    Args:
        name: Server name
        version: Server version
        description: Server description
        include_instructions: Whether to include server instructions for LLMs

    Returns:
        Configured FastMCP server instance

    Raises:
        ImportError: If FastMCP is not available
    """
    if not _FASTMCP_AVAILABLE:
        raise ImportError(
            "FastMCP is required for MCP server functionality. "
            "Install it with: pip install fastmcp"
        )

    if description is None:
        description = (
            "MCP server for diagramaid: Generate, validate, and manipulate "
            "Mermaid diagrams with AI-powered features and auto-repair workflow"
        )

    # Create FastMCP server instance with instructions
    server_kwargs: dict[str, Any] = {
        "name": name,
        "version": version,
    }

    # Add instructions if requested (helps LLMs understand server capabilities)
    if include_instructions:
        server_kwargs["instructions"] = SERVER_INSTRUCTIONS

    mcp = FastMCP(**server_kwargs)

    # Register all MCP components
    register_all_tools(mcp)
    register_all_resources(mcp)
    register_all_prompts(mcp)

    # Register extended components (including repair workflow)
    register_extended_tools(mcp)
    register_extended_resources(mcp)
    register_extended_prompts(mcp)

    logger.info(
        f"Created MCP server '{name}' v{version} with tools, resources, prompts, "
        f"and repair workflow"
    )
    return mcp


async def run_server(
    transport: str = "stdio", host: str = "localhost", port: int = 8000, **kwargs: Any
) -> None:
    """
    Run the MCP server with the specified transport.

    Args:
        transport: Transport type ("stdio", "sse", "websocket")
        host: Host address for network transports
        port: Port number for network transports
        **kwargs: Additional server configuration

    Raises:
        ImportError: If FastMCP is not available
    """
    if not _FASTMCP_AVAILABLE:
        raise ImportError(
            "FastMCP is required for MCP server functionality. "
            "Install it with: pip install fastmcp"
        )

    mcp = create_mcp_server(**kwargs)

    if transport == "stdio":
        logger.info("Starting MCP server with stdio transport")
        await mcp.run_stdio()
    elif transport == "sse":
        logger.info(f"Starting MCP server with SSE transport on {host}:{port}")
        await mcp.run_sse(host=host, port=port)
    elif transport == "websocket":
        logger.info(f"Starting MCP server with WebSocket transport on {host}:{port}")
        await mcp.run_websocket(host=host, port=port)
    else:
        raise ValueError(f"Unsupported transport: {transport}")


def main() -> None:
    """
    Main entry point for the MCP server CLI.
    """
    parser = argparse.ArgumentParser(
        description="MCP server for diagramaid",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio transport (default)
  diagramaid-mcp

  # Run with SSE transport
  diagramaid-mcp --transport sse --port 8080

  # Run with WebSocket transport
  diagramaid-mcp --transport websocket --host 0.0.0.0 --port 9000
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "websocket"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host address for network transports (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for network transports (default: 8000)",
    )
    parser.add_argument(
        "--name",
        default="diagramaid",
        help="Server name (default: diagramaid)",
    )
    parser.add_argument(
        "--version",
        default="1.0.0",
        help="Server version (default: 1.0.0)",
    )
    parser.add_argument(
        "--description",
        help="Server description",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Run the server
    try:
        asyncio.run(
            run_server(
                transport=args.transport,
                host=args.host,
                port=args.port,
                name=args.name,
                version=args.version,
                description=args.description,
            )
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
