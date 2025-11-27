"""
Unit tests for interactive.websocket.message_dispatcher module.

Tests the MessageDispatcher class.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from mermaid_render.interactive.websocket.message_dispatcher import MessageDispatcher


@pytest.mark.unit
class TestMessageDispatcher:
    """Unit tests for MessageDispatcher class."""

    def test_initialization(self) -> None:
        """Test MessageDispatcher initialization."""
        dispatcher = MessageDispatcher()
        assert dispatcher is not None

    def test_register_handler(self) -> None:
        """Test registering message handler."""
        dispatcher = MessageDispatcher()
        handler = Mock()
        dispatcher.register("test_type", handler)
        assert "test_type" in dispatcher.handlers

    def test_unregister_handler(self) -> None:
        """Test unregistering message handler."""
        dispatcher = MessageDispatcher()
        handler = Mock()
        dispatcher.register("test_type", handler)
        dispatcher.unregister("test_type")
        assert "test_type" not in dispatcher.handlers

    @pytest.mark.asyncio
    async def test_dispatch_message(self) -> None:
        """Test dispatching message to handler."""
        dispatcher = MessageDispatcher()
        handler = AsyncMock()
        dispatcher.register("update", handler)

        message = {"type": "update", "data": {"id": "123"}}
        await dispatcher.dispatch(message)

        handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_unknown_type(self) -> None:
        """Test dispatching message with unknown type."""
        dispatcher = MessageDispatcher()

        message = {"type": "unknown", "data": {}}
        # Should not raise
        await dispatcher.dispatch(message)

    @pytest.mark.asyncio
    async def test_dispatch_with_context(self) -> None:
        """Test dispatching message with context."""
        dispatcher = MessageDispatcher()
        handler = AsyncMock()
        dispatcher.register("action", handler)

        message = {"type": "action", "data": {}}
        context = {"session_id": "sess123"}
        await dispatcher.dispatch(message, context=context)

        handler.assert_called_once()

    def test_has_handler(self) -> None:
        """Test checking if handler exists."""
        dispatcher = MessageDispatcher()
        handler = Mock()
        dispatcher.register("test", handler)

        assert dispatcher.has_handler("test")
        assert not dispatcher.has_handler("nonexistent")
