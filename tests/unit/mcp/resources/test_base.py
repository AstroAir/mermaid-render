"""
Unit tests for mcp.resources.base module.

Tests for base utilities and ResourceError.
"""

import pytest

from diagramaid.mcp.resources.base import (
    _FASTMCP_AVAILABLE,
    ResourceError,
)


@pytest.mark.unit
class TestResourceError:
    """Tests for ResourceError exception."""

    def test_resource_error_is_exception(self):
        """Test ResourceError is an Exception."""
        assert issubclass(ResourceError, Exception)

    def test_resource_error_with_message(self):
        """Test ResourceError with message."""
        error = ResourceError("Test error message")
        assert str(error) == "Test error message"

    def test_resource_error_can_be_raised(self):
        """Test ResourceError can be raised."""
        with pytest.raises(ResourceError):
            raise ResourceError("Test error")


@pytest.mark.unit
class TestFastMCPAvailability:
    """Tests for FastMCP availability check."""

    def test_fastmcp_available_is_bool(self):
        """Test _FASTMCP_AVAILABLE is a boolean."""
        assert isinstance(_FASTMCP_AVAILABLE, bool)

    def test_module_imports(self):
        """Test module can be imported."""
        from diagramaid.mcp.resources import base

        assert hasattr(base, "_FASTMCP_AVAILABLE")
        assert hasattr(base, "ResourceError")
        assert hasattr(base, "logger")
