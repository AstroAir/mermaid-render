"""
Message dispatcher for the interactive diagram builder.

This module provides message routing and handling for WebSocket messages.
"""

from datetime import datetime
from typing import Any

from ..models import Position, Size
from .broadcast_service import BroadcastService
from .session_manager import DiagramSession


class MessageDispatcher:
    """
    Dispatches and handles WebSocket messages.

    Routes incoming messages to appropriate handlers based on message type.
    """

    def __init__(self, broadcast_service: BroadcastService) -> None:
        """
        Initialize message dispatcher.

        Args:
            broadcast_service: BroadcastService for sending responses
        """
        self.broadcast_service = broadcast_service

        # Message type to handler mapping
        self._handlers: dict[str, Any] = {
            "element_update": self._handle_element_update,
            "connection_update": self._handle_connection_update,
            "cursor_update": self._handle_cursor_update,
            "selection_update": self._handle_selection_update,
            "chat_message": self._handle_chat_message,
            "ping": self._handle_ping,
        }

    async def dispatch(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """
        Dispatch a message to the appropriate handler.

        Args:
            session: DiagramSession context
            message: Message to dispatch
        """
        message_type = message.get("type")
        handler = self._handlers.get(message_type)

        if handler:
            await handler(session, message)

    async def _handle_element_update(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """Handle element update message."""
        element_id = message.get("element_id")
        updates = message.get("updates", {})

        if not element_id or not updates:
            return

        # Build update parameters
        update_params: dict[str, Any] = {}

        if "label" in updates:
            update_params["label"] = updates["label"]
        if "position" in updates:
            update_params["position"] = Position.from_dict(updates["position"])
        if "size" in updates:
            update_params["size"] = Size.from_dict(updates["size"])
        if "properties" in updates:
            update_params["properties"] = updates["properties"]
        if "style" in updates:
            update_params["style"] = updates["style"]

        # Apply updates to builder
        success = session.builder.update_element(element_id, **update_params)

        if success:
            # Broadcast update to other clients
            broadcast_message = {
                "type": "element_updated",
                "element_id": element_id,
                "updates": updates,
                "timestamp": datetime.now().isoformat(),
            }
            disconnected = await self.broadcast_service.send_to_session(
                session, broadcast_message
            )

            # Clean up disconnected clients
            for client in disconnected:
                session.remove_client(client)

    async def _handle_connection_update(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """Handle connection update message."""
        connection_id = message.get("connection_id")
        updates = message.get("updates", {})

        if not connection_id or not updates:
            return

        # Build update parameters
        update_params: dict[str, Any] = {}

        if "label" in updates:
            update_params["label"] = updates["label"]
        if "connection_type" in updates:
            update_params["connection_type"] = updates["connection_type"]
        if "style" in updates:
            update_params["style"] = updates["style"]
        if "properties" in updates:
            update_params["properties"] = updates["properties"]

        # Apply updates to builder
        success = session.builder.update_connection(connection_id, **update_params)

        if success:
            # Broadcast update to other clients
            broadcast_message = {
                "type": "connection_updated",
                "connection_id": connection_id,
                "updates": updates,
                "timestamp": datetime.now().isoformat(),
            }
            disconnected = await self.broadcast_service.send_to_session(
                session, broadcast_message
            )

            # Clean up disconnected clients
            for client in disconnected:
                session.remove_client(client)

    async def _handle_cursor_update(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """Handle cursor position update."""
        cursor_data = {
            "type": "cursor_update",
            "client_id": message.get("client_id"),
            "position": message.get("position"),
            "timestamp": datetime.now().isoformat(),
        }
        disconnected = await self.broadcast_service.send_to_session(
            session, cursor_data
        )

        # Clean up disconnected clients
        for client in disconnected:
            session.remove_client(client)

    async def _handle_selection_update(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """Handle selection update."""
        selection_data = {
            "type": "selection_update",
            "client_id": message.get("client_id"),
            "selected_elements": message.get("selected_elements", []),
            "timestamp": datetime.now().isoformat(),
        }
        disconnected = await self.broadcast_service.send_to_session(
            session, selection_data
        )

        # Clean up disconnected clients
        for client in disconnected:
            session.remove_client(client)

    async def _handle_chat_message(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """Handle chat message."""
        chat_data = {
            "type": "chat_message",
            "client_id": message.get("client_id"),
            "username": message.get("username", "Anonymous"),
            "message": message.get("message", ""),
            "timestamp": datetime.now().isoformat(),
        }
        disconnected = await self.broadcast_service.send_to_session(
            session, chat_data
        )

        # Clean up disconnected clients
        for client in disconnected:
            session.remove_client(client)

    async def _handle_ping(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """Handle ping message (keep-alive)."""
        # Update session activity
        session.touch()

    def register_handler(
        self, message_type: str, handler: Any
    ) -> None:
        """
        Register a custom message handler.

        Args:
            message_type: Type of message to handle
            handler: Async handler function
        """
        self._handlers[message_type] = handler

    def unregister_handler(self, message_type: str) -> bool:
        """
        Unregister a message handler.

        Args:
            message_type: Type of message handler to remove

        Returns:
            True if handler was removed
        """
        if message_type in self._handlers:
            del self._handlers[message_type]
            return True
        return False
