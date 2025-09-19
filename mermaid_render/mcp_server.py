"""
Main entry point for the mermaid-render MCP server.

This module provides the main() function that serves as the entry point
for the mermaid-render-mcp command.
"""

from .mcp.server import main

if __name__ == "__main__":
    main()
