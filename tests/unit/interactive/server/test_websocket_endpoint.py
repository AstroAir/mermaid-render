"""
Unit tests for interactive.server.websocket_endpoint module.

Tests the WebSocket endpoint setup.
"""

import pytest
from unittest.mock import Mock

from mermaid_render.interactive.server.websocket_endpoint import setup_websocket_endpoint
from mermaid_render.interactive.websocket import WebSocketHandler


@pytest.mark.unit
class TestWebSocketEndpoint:
    """Unit tests for WebSocket endpoint."""

    def test_setup_websocket_endpoint(self) -> None:
        """Test setting up WebSocket endpoint."""
        mock_app = Mock()
        websocket_handler = WebSocketHandler()
        setup_websocket_endpoint(mock_app, websocket_handler)
        # Should add WebSocket route
        assert mock_app.websocket.called

    def test_websocket_path(self) -> None:
        """Test WebSocket endpoint path."""
        mock_app = Mock()
        websocket_handler = WebSocketHandler()
        setup_websocket_endpoint(mock_app, websocket_handler)
        # Should set up at expected path /ws/{session_id}
        mock_app.websocket.assert_called_with("/ws/{session_id}")
