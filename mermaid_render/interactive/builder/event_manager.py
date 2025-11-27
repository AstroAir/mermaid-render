"""
Event management for the interactive diagram builder.

This module provides centralized event handling for diagram changes.
"""

from collections.abc import Callable
from typing import Any


class EventManager:
    """
    Centralized event manager for diagram builder events.

    Provides a unified interface for registering and dispatching
    events related to diagram modifications.
    """

    def __init__(self) -> None:
        """Initialize event manager."""
        self._handlers: dict[str, list[Callable[..., Any]]] = {
            "element_added": [],
            "element_updated": [],
            "element_removed": [],
            "connection_added": [],
            "connection_updated": [],
            "connection_removed": [],
            "diagram_changed": [],
            "metadata_updated": [],
        }

    def register(self, event_type: str, handler: Callable[..., Any]) -> None:
        """
        Register an event handler.

        Args:
            event_type: Type of event to handle
            handler: Callback function to invoke
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unregister(self, event_type: str, handler: Callable[..., Any]) -> bool:
        """
        Unregister an event handler.

        Args:
            event_type: Type of event
            handler: Handler to remove

        Returns:
            True if handler was removed
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            return True
        return False

    def emit(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event to all registered handlers.

        Args:
            event_type: Type of event to emit
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(*args, **kwargs)

    def clear(self, event_type: str | None = None) -> None:
        """
        Clear event handlers.

        Args:
            event_type: Specific event type to clear, or None to clear all
        """
        if event_type is None:
            for key in self._handlers:
                self._handlers[key] = []
        elif event_type in self._handlers:
            self._handlers[event_type] = []

    def get_handler_count(self, event_type: str) -> int:
        """Get number of handlers for an event type."""
        return len(self._handlers.get(event_type, []))

    def get_event_types(self) -> list[str]:
        """Get list of registered event types."""
        return list(self._handlers.keys())
