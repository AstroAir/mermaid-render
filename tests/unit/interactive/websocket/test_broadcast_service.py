"""
Unit tests for interactive.websocket.broadcast_service module.

Tests the BroadcastService class.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from mermaid_render.interactive.websocket.broadcast_service import BroadcastService


@pytest.mark.unit
class TestBroadcastService:
    """Unit tests for BroadcastService class."""

    def test_initialization(self) -> None:
        """Test BroadcastService initialization."""
        service = BroadcastService()
        assert service is not None
        assert service.debounce_delay == 0.1

    def test_initialization_with_custom_delay(self) -> None:
        """Test BroadcastService initialization with custom debounce delay."""
        service = BroadcastService(debounce_delay=0.5)
        assert service.debounce_delay == 0.5

    @pytest.mark.asyncio
    async def test_send_to_client_success(self) -> None:
        """Test sending message to client successfully."""
        service = BroadcastService()
        mock_ws = AsyncMock()
        result = await service.send_to_client(mock_ws, {"type": "test"})
        assert result is True
        mock_ws.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_client_failure(self) -> None:
        """Test sending message to client with failure."""
        service = BroadcastService()
        mock_ws = AsyncMock()
        mock_ws.send_text.side_effect = Exception("Connection closed")
        result = await service.send_to_client(mock_ws, {"type": "test"})
        assert result is False

    @pytest.mark.asyncio
    async def test_send_error(self) -> None:
        """Test sending error message to client."""
        service = BroadcastService()
        mock_ws = AsyncMock()
        result = await service.send_error(mock_ws, "Test error", "test_code")
        assert result is True
        mock_ws.send_text.assert_called_once()
