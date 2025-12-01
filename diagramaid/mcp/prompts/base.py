"""
Base utilities for MCP prompts.

This module provides common utilities and FastMCP availability check.
"""

import logging

try:
    from fastmcp import Context, FastMCP
    from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

    _FASTMCP_AVAILABLE = True
except ImportError:
    FastMCP = None
    Context = None
    Message = None
    PromptMessage = None
    TextContent = None
    _FASTMCP_AVAILABLE = False

logger = logging.getLogger(__name__)

__all__ = [
    "_FASTMCP_AVAILABLE",
    "Context",
    "FastMCP",
    "Message",
    "PromptMessage",
    "TextContent",
    "logger",
]
