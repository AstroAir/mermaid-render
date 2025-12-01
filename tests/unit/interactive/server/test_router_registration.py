"""
Unit tests for interactive.server.router_registration module.

Tests the router registration functions.
"""

import pytest
from unittest.mock import Mock

from diagramaid.interactive.server.router_registration import register_api_routers
from diagramaid.interactive.websocket import WebSocketHandler


@pytest.mark.unit
class TestRouterRegistration:
    """Unit tests for router registration."""

    def test_register_api_routers(self) -> None:
        """Test registering API routers."""
        mock_app = Mock()
        sessions: dict = {}
        websocket_handler = WebSocketHandler()
        renderer = Mock()
        validator = Mock()
        register_api_routers(mock_app, sessions, websocket_handler, renderer, validator)
        # Should include routers
        assert mock_app.include_router.called

    def test_registers_multiple_routers(self) -> None:
        """Test that multiple routers are registered."""
        mock_app = Mock()
        sessions: dict = {}
        websocket_handler = WebSocketHandler()
        renderer = Mock()
        validator = Mock()
        register_api_routers(mock_app, sessions, websocket_handler, renderer, validator)
        # Should have called include_router multiple times (3 routers)
        assert mock_app.include_router.call_count >= 3
