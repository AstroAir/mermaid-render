"""
Unit tests for interactive.websocket.broadcast_service module.

Tests the BroadcastService class.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from mermaid_render.interactive.websocket.broadcast_service import BroadcastService


@pytest.mark.unit
class TestBroadcastService:
    """Unit tests for BroadcastService class."""

    def test_initialization(self) -> None:
        """Test BroadcastService initialization."""
        service = BroadcastService()
        assert service is not None

    def test_subscribe(self) -> None:
        """Test subscribing to channel."""
        service = BroadcastService()
        mock_websocket = Mock()
        service.subscribe("channel1", mock_websocket)
        assert mock_websocket in service.get_subscribers("channel1")

    def test_unsubscribe(self) -> None:
        """Test unsubscribing from channel."""
        service = BroadcastService()
        mock_websocket = Mock()
        service.subscribe("channel1", mock_websocket)
        service.unsubscribe("channel1", mock_websocket)
        assert mock_websocket not in service.get_subscribers("channel1")

    @pytest.mark.asyncio
    async def test_broadcast_to_channel(self) -> None:
        """Test broadcasting to channel."""
        service = BroadcastService()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()

        service.subscribe("updates", mock_ws1)
        service.subscribe("updates", mock_ws2)

        await service.broadcast("updates", {"type": "update"})

        mock_ws1.send_json.assert_called()
        mock_ws2.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_broadcast_to_empty_channel(self) -> None:
        """Test broadcasting to empty channel."""
        service = BroadcastService()

        # Should not raise
        await service.broadcast("empty_channel", {"data": "test"})

    def test_get_subscribers(self) -> None:
        """Test getting subscribers for channel."""
        service = BroadcastService()
        mock_ws = Mock()
        service.subscribe("test", mock_ws)

        subscribers = service.get_subscribers("test")
        assert len(subscribers) == 1

    def test_get_subscribers_empty(self) -> None:
        """Test getting subscribers for non-existent channel."""
        service = BroadcastService()
        subscribers = service.get_subscribers("nonexistent")
        assert len(subscribers) == 0

    def test_channel_count(self) -> None:
        """Test counting active channels."""
        service = BroadcastService()
        mock_ws = Mock()

        service.subscribe("channel1", mock_ws)
        service.subscribe("channel2", mock_ws)

        assert service.channel_count() >= 2

    @pytest.mark.asyncio
    async def test_broadcast_all(self) -> None:
        """Test broadcasting to all channels."""
        service = BroadcastService()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()

        service.subscribe("channel1", mock_ws1)
        service.subscribe("channel2", mock_ws2)

        await service.broadcast_all({"type": "global_update"})

        mock_ws1.send_json.assert_called()
        mock_ws2.send_json.assert_called()
