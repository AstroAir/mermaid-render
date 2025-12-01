"""
Unit tests for interactive.websocket.websocket_handler module.

Tests the WebSocketHandler class.
"""

import pytest

from diagramaid.interactive.websocket.websocket_handler import WebSocketHandler


@pytest.mark.unit
class TestWebSocketHandler:
    """Unit tests for WebSocketHandler class."""

    def test_initialization(self) -> None:
        """Test WebSocketHandler initialization."""
        handler = WebSocketHandler()
        assert handler is not None
        assert handler._session_manager is not None
        assert handler._broadcast_service is not None
        assert handler._message_dispatcher is not None

    def test_initialization_with_max_sessions(self) -> None:
        """Test WebSocketHandler initialization with custom max sessions."""
        handler = WebSocketHandler(max_sessions=50)
        assert handler._session_manager.max_sessions == 50

    def test_sessions_property(self) -> None:
        """Test sessions property returns session manager sessions."""
        handler = WebSocketHandler()
        assert handler.sessions == handler._session_manager.sessions

    def test_get_session_info_nonexistent(self) -> None:
        """Test getting info for non-existent session."""
        handler = WebSocketHandler()
        info = handler.get_session_info("nonexistent")
        assert info is None

    def test_get_all_sessions_empty(self) -> None:
        """Test getting all sessions when empty."""
        handler = WebSocketHandler()
        sessions = handler.get_all_sessions()
        assert sessions == []

    def test_get_client_session_unknown(self) -> None:
        """Test getting session for unknown client."""
        from unittest.mock import Mock

        handler = WebSocketHandler()
        mock_ws = Mock()
        session_id = handler.get_client_session(mock_ws)
        assert session_id is None
