"""
Unit tests for mcp.prompts.base module.

Tests for base utilities and FastMCP availability.
"""

import pytest

from mermaid_render.mcp.prompts.base import _FASTMCP_AVAILABLE


@pytest.mark.unit
class TestFastMCPAvailability:
    """Tests for FastMCP availability check."""

    def test_fastmcp_available_is_bool(self):
        """Test _FASTMCP_AVAILABLE is a boolean."""
        assert isinstance(_FASTMCP_AVAILABLE, bool)

    def test_module_imports(self):
        """Test module can be imported."""
        from mermaid_render.mcp.prompts import base

        assert hasattr(base, "_FASTMCP_AVAILABLE")
        assert hasattr(base, "logger")
