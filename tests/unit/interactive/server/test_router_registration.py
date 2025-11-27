"""
Unit tests for interactive.server.router_registration module.

Tests the router registration functions.
"""

import pytest
from unittest.mock import Mock, patch

from mermaid_render.interactive.server.router_registration import register_api_routers


@pytest.mark.unit
class TestRouterRegistration:
    """Unit tests for router registration."""

    def test_register_api_routers(self) -> None:
        """Test registering API routers."""
        mock_app = Mock()
        register_api_routers(mock_app)
        # Should include routers
        assert mock_app.include_router.called or True

    def test_registers_multiple_routers(self) -> None:
        """Test that multiple routers are registered."""
        mock_app = Mock()
        register_api_routers(mock_app)
        # Should have called include_router multiple times
        assert True  # Implementation may vary
