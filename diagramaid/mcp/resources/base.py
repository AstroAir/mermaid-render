"""
Base utilities for MCP resources.

This module provides common utilities and FastMCP availability check.
"""

import logging

try:
    from fastmcp import Context, FastMCP

    _FASTMCP_AVAILABLE = True
except ImportError:
    FastMCP = None
    Context = None
    _FASTMCP_AVAILABLE = False


class ResourceError(Exception):
    """Resource error for MCP operations."""

    pass


logger = logging.getLogger(__name__)

__all__ = [
    "_FASTMCP_AVAILABLE",
    "Context",
    "FastMCP",
    "ResourceError",
    "logger",
]
