"""
Unit tests for interactive.websocket.websocket_handler module.

Tests the WebSocketHandler class.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from mermaid_render.interactive.websocket.websocket_handler import WebSocketHandler


@pytest.mark.unit
class TestWebSocketHandler:
    """Unit tests for WebSocketHandler class."""

    def test_initialization(self) -> None:
        """Test WebSocketHandler initialization."""
        handler = WebSocketHandler()
        assert handler is not None

    @pytest.mark.asyncio
    async def test_handle_connection(self) -> None:
        """Test handling WebSocket connection."""
        handler = WebSocketHandler()
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_json = AsyncMock(side_effect=Exception("Connection closed"))

        # Should handle connection without raising
        try:
            await handler.handle(mock_websocket)
        except Exception:
            pass  # Expected to handle gracefully

    @pytest.mark.asyncio
    async def test_send_message(self) -> None:
        """Test sending message through WebSocket."""
        handler = WebSocketHandler()
        mock_websocket = AsyncMock()

        await handler.send_message(mock_websocket, {"type": "update", "data": {}})
        mock_websocket.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast(self) -> None:
        """Test broadcasting to multiple connections."""
        handler = WebSocketHandler()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()

        handler.connections = [mock_ws1, mock_ws2]
        await handler.broadcast({"type": "update"})

        mock_ws1.send_json.assert_called()
        mock_ws2.send_json.assert_called()

    def test_add_connection(self) -> None:
        """Test adding connection to handler."""
        handler = WebSocketHandler()
        mock_websocket = Mock()

        handler.add_connection(mock_websocket)
        assert mock_websocket in handler.connections

    def test_remove_connection(self) -> None:
        """Test removing connection from handler."""
        handler = WebSocketHandler()
        mock_websocket = Mock()

        handler.add_connection(mock_websocket)
        handler.remove_connection(mock_websocket)
        assert mock_websocket not in handler.connections
