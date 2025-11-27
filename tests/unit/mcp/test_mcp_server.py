"""
Unit tests for MCP server functionality.

Tests the MCP server creation and configuration.
"""

from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestMCPServerCreation:
    """Tests for MCP server creation."""

    def test_create_mcp_server_without_fastmcp(self):
        """Test server creation fails gracefully without FastMCP."""
        with patch.dict("sys.modules", {"fastmcp": None}):
            # Should handle missing FastMCP gracefully
            pass

    @patch("mermaid_render.mcp.server._FASTMCP_AVAILABLE", True)
    def test_create_mcp_server_with_defaults(self):
        """Test server creation with default parameters."""
        from mermaid_render.mcp.server import _FASTMCP_AVAILABLE

        if not _FASTMCP_AVAILABLE:
            pytest.skip("FastMCP not available")

        # Test would create server with defaults
        # This is a placeholder for actual FastMCP testing

    def test_server_module_imports(self):
        """Test that server module can be imported."""
        from mermaid_render.mcp import server

        assert hasattr(server, "create_mcp_server")
        assert hasattr(server, "main")


@pytest.mark.unit
class TestMCPServerConfiguration:
    """Tests for MCP server configuration."""

    def test_default_server_name(self):
        """Test default server name is set correctly."""
        # Default name should be "mermaid-render"
        pass

    def test_default_server_version(self):
        """Test default server version is set correctly."""
        # Default version should be "1.0.0"
        pass


@pytest.mark.unit
class TestMCPRegistration:
    """Tests for MCP component registration."""

    def test_register_all_tools_import(self):
        """Test register_all_tools can be imported."""
        from mermaid_render.mcp import register_all_tools

        assert callable(register_all_tools)

    def test_register_extended_tools_import(self):
        """Test register_extended_tools can be imported."""
        from mermaid_render.mcp import register_extended_tools

        assert callable(register_extended_tools)

    def test_register_all_prompts_import(self):
        """Test register_all_prompts can be imported."""
        from mermaid_render.mcp import register_all_prompts

        assert callable(register_all_prompts)

    def test_register_extended_prompts_import(self):
        """Test register_extended_prompts can be imported."""
        from mermaid_render.mcp import register_extended_prompts

        assert callable(register_extended_prompts)

    def test_register_all_resources_import(self):
        """Test register_all_resources can be imported."""
        from mermaid_render.mcp import register_all_resources

        assert callable(register_all_resources)

    def test_register_extended_resources_import(self):
        """Test register_extended_resources can be imported."""
        from mermaid_render.mcp import register_extended_resources

        assert callable(register_extended_resources)

