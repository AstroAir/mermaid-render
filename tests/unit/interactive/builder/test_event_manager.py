"""
Unit tests for interactive.builder.event_manager module.

Tests the EventManager class for handling diagram events.
"""

import pytest
from unittest.mock import Mock

from mermaid_render.interactive.builder.event_manager import EventManager


@pytest.mark.unit
class TestEventManager:
    """Unit tests for EventManager class."""

    def test_initialization(self) -> None:
        """Test EventManager initialization."""
        manager = EventManager()
        assert manager is not None

    def test_subscribe(self) -> None:
        """Test subscribing to events."""
        manager = EventManager()
        callback = Mock()
        manager.register("element_added", callback)
        # Verify subscription was added
        assert manager.get_handler_count("element_added") >= 1

    def test_unsubscribe(self) -> None:
        """Test unsubscribing from events."""
        manager = EventManager()
        callback = Mock()
        manager.register("element_added", callback)
        manager.unregister("element_added", callback)
        # Callback should not be called after unsubscribe
        manager.emit("element_added", {"id": "test"})
        callback.assert_not_called()

    def test_emit_event(self) -> None:
        """Test emitting events."""
        manager = EventManager()
        callback = Mock()
        manager.register("element_added", callback)
        manager.emit("element_added", {"id": "test_element"})
        callback.assert_called_once_with({"id": "test_element"})

    def test_emit_to_multiple_subscribers(self) -> None:
        """Test emitting to multiple subscribers."""
        manager = EventManager()
        callback1 = Mock()
        callback2 = Mock()
        manager.register("element_added", callback1)
        manager.register("element_added", callback2)
        manager.emit("element_added", {"id": "test"})
        callback1.assert_called_once()
        callback2.assert_called_once()

    def test_emit_nonexistent_event(self) -> None:
        """Test emitting event with no subscribers."""
        manager = EventManager()
        # Should not raise error
        manager.emit("nonexistent_event", {"data": "test"})

    def test_clear_subscribers(self) -> None:
        """Test clearing all subscribers."""
        manager = EventManager()
        callback = Mock()
        manager.register("element_added", callback)
        manager.register("element_updated", callback)
        manager.clear()
        manager.emit("element_added", {})
        manager.emit("element_updated", {})
        callback.assert_not_called()

    def test_subscriber_error_handling(self) -> None:
        """Test error handling when subscriber raises exception."""
        manager = EventManager()

        def failing_callback(data: dict) -> None:
            raise ValueError("Test error")

        good_callback = Mock()
        manager.register("element_added", failing_callback)
        manager.register("element_added", good_callback)
        # Note: Current implementation does not catch exceptions
        # This test verifies the first callback raises
        with pytest.raises(ValueError):
            manager.emit("element_added", {"data": "test"})
