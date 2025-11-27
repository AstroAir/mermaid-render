"""
FastMCP server implementation for mermaid-render.

This module creates and configures the MCP server that exposes mermaid-render
functionality through the Model Context Protocol.
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


def create_mcp_server(
    name: str = "mermaid-render",
    version: str = "1.0.0",
    description: str | None = None,
) -> Any:
    """
    Create and configure the MCP server for mermaid-render.

    Args:
        name: Server name
        version: Server version
        description: Server description

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
            "MCP server for mermaid-render: Generate, validate, and manipulate "
            "Mermaid diagrams with AI-powered features"
        )

    # Create FastMCP server instance (description not supported in current version)
    mcp = FastMCP(name=name, version=version)

    # Register all MCP components
    register_all_tools(mcp)
    register_all_resources(mcp)
    register_all_prompts(mcp)

    # Register extended components
    register_extended_tools(mcp)
    register_extended_resources(mcp)
    register_extended_prompts(mcp)

    logger.info(
        f"Created MCP server '{name}' v{version} with tools, resources, and prompts"
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
        description="MCP server for mermaid-render",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio transport (default)
  mermaid-render-mcp

  # Run with SSE transport
  mermaid-render-mcp --transport sse --port 8080

  # Run with WebSocket transport
  mermaid-render-mcp --transport websocket --host 0.0.0.0 --port 9000
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
        default="mermaid-render",
        help="Server name (default: mermaid-render)",
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
