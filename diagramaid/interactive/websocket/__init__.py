"""
WebSocket package for the interactive diagram builder.

This package provides WebSocket management for real-time updates
and collaborative editing capabilities.
"""

from .broadcast_service import BroadcastService
from .message_dispatcher import MessageDispatcher
from .session_manager import DiagramSession, SessionManager
from .websocket_handler import WebSocketHandler

__all__ = [
    "WebSocketHandler",
    "DiagramSession",
    "SessionManager",
    "MessageDispatcher",
    "BroadcastService",
]
