"""
Unit tests for interactive.builder.event_manager module.

Tests the EventManager class for handling diagram events.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

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
        
        manager.subscribe("element_added", callback)
        
        # Verify subscription was added
        assert "element_added" in manager._subscribers

    def test_unsubscribe(self) -> None:
        """Test unsubscribing from events."""
        manager = EventManager()
        callback = Mock()
        
        manager.subscribe("element_added", callback)
        manager.unsubscribe("element_added", callback)
        
        # Callback should not be called after unsubscribe
        manager.emit("element_added", {"id": "test"})
        callback.assert_not_called()

    def test_emit_event(self) -> None:
        """Test emitting events."""
        manager = EventManager()
        callback = Mock()
        
        manager.subscribe("element_added", callback)
        manager.emit("element_added", {"id": "test_element"})
        
        callback.assert_called_once_with({"id": "test_element"})

    def test_emit_to_multiple_subscribers(self) -> None:
        """Test emitting to multiple subscribers."""
        manager = EventManager()
        callback1 = Mock()
        callback2 = Mock()
        
        manager.subscribe("element_added", callback1)
        manager.subscribe("element_added", callback2)
        
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
        
        manager.subscribe("event1", callback)
        manager.subscribe("event2", callback)
        
        manager.clear()
        
        manager.emit("event1", {})
        manager.emit("event2", {})
        
        callback.assert_not_called()

    def test_subscriber_error_handling(self) -> None:
        """Test error handling when subscriber raises exception."""
        manager = EventManager()
        
        def failing_callback(data):
            raise ValueError("Test error")
        
        good_callback = Mock()
        
        manager.subscribe("test_event", failing_callback)
        manager.subscribe("test_event", good_callback)
        
        # Should not raise, and should still call other subscribers
        manager.emit("test_event", {"data": "test"})
        
        good_callback.assert_called_once()
