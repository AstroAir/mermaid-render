"""
Unit tests for interactive.websocket.message_dispatcher module.

Tests the MessageDispatcher class.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from mermaid_render.interactive.websocket.broadcast_service import BroadcastService
from mermaid_render.interactive.websocket.message_dispatcher import MessageDispatcher


@pytest.mark.unit
class TestMessageDispatcher:
    """Unit tests for MessageDispatcher class."""

    def test_initialization(self) -> None:
        """Test MessageDispatcher initialization."""
        broadcast_service = BroadcastService()
        dispatcher = MessageDispatcher(broadcast_service)
        assert dispatcher is not None
        assert dispatcher.broadcast_service is broadcast_service

    def test_register_handler(self) -> None:
        """Test registering message handler."""
        broadcast_service = BroadcastService()
        dispatcher = MessageDispatcher(broadcast_service)
        handler = Mock()
        dispatcher.register_handler("test_type", handler)
        assert "test_type" in dispatcher._handlers

    def test_unregister_handler(self) -> None:
        """Test unregistering message handler."""
        broadcast_service = BroadcastService()
        dispatcher = MessageDispatcher(broadcast_service)
        handler = Mock()
        dispatcher.register_handler("test_type", handler)
        result = dispatcher.unregister_handler("test_type")
        assert result is True
        assert "test_type" not in dispatcher._handlers

    def test_unregister_nonexistent_handler(self) -> None:
        """Test unregistering non-existent handler."""
        broadcast_service = BroadcastService()
        dispatcher = MessageDispatcher(broadcast_service)
        result = dispatcher.unregister_handler("nonexistent")
        assert result is False

    def test_default_handlers_registered(self) -> None:
        """Test that default handlers are registered."""
        broadcast_service = BroadcastService()
        dispatcher = MessageDispatcher(broadcast_service)
        assert "element_update" in dispatcher._handlers
        assert "connection_update" in dispatcher._handlers
        assert "cursor_update" in dispatcher._handlers
        assert "ping" in dispatcher._handlers
