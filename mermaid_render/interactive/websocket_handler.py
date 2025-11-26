"""
WebSocket handler for real-time collaboration.

This module provides WebSocket management for real-time updates
and collaborative editing capabilities.
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from fastapi import WebSocket

from .builder import DiagramBuilder
from .security import InputSanitizer, SecurityValidator, websocket_rate_limiter


@dataclass
class DiagramSession:
    """Represents an active diagram editing session."""

    session_id: str
    builder: DiagramBuilder
    created_at: datetime
    updated_at: datetime
    connected_clients: set[WebSocket]

    def __init__(self, session_id: str, builder: DiagramBuilder) -> None:
        self.session_id = session_id
        self.builder = builder
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.connected_clients = set()

    def add_client(self, websocket: WebSocket) -> None:
        """Add client to session."""
        self.connected_clients.add(websocket)
        self.updated_at = datetime.now()

    def remove_client(self, websocket: WebSocket) -> None:
        """Remove client from session."""
        self.connected_clients.discard(websocket)
        self.updated_at = datetime.now()

    def get_client_count(self) -> int:
        """Get number of connected clients."""
        return len(self.connected_clients)


class WebSocketHandler:
    """
    Handles WebSocket connections for real-time collaboration.

    Manages client connections, message broadcasting, and session
    synchronization for collaborative diagram editing.
    """

    def __init__(self) -> None:
        """Initialize WebSocket handler."""
        self.sessions: dict[str, DiagramSession] = {}
        self.client_sessions: dict[WebSocket, str] = {}
        # Removed dependency on external debouncer

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """
        Connect client to session.

        Args:
            websocket: WebSocket connection
            session_id: Session ID to join
        """
        try:
            # Validate session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)

            # Check rate limit
            client_ip = websocket.client.host if websocket.client else "unknown"
            if not websocket_rate_limiter.is_allowed(client_ip):
                await websocket.close(code=1008, reason="Rate limit exceeded")
                return

            # Validate origin if present
            origin = websocket.headers.get("origin")
            if not SecurityValidator.validate_websocket_origin(origin):
                await websocket.close(code=1008, reason="Invalid origin")
                return

            await websocket.accept()

            # Create session if it doesn't exist
            if session_id not in self.sessions:
                from .builder import DiagramBuilder, DiagramType

                builder = DiagramBuilder(DiagramType.FLOWCHART)
                self.sessions[session_id] = DiagramSession(session_id, builder)

            # Add client to session
            session = self.sessions[session_id]
            session.add_client(websocket)
            self.client_sessions[websocket] = session_id

            # Send current state to new client
            await self._send_current_state(websocket, session)

            # Notify other clients about new connection
            await self._broadcast_client_update(session_id)

        except ValueError as e:
            # Invalid session ID or other validation error
            await websocket.close(code=1008, reason=str(e))
        except Exception:
            # Unexpected error during connection
            await websocket.close(code=1011, reason="Internal server error")

    async def broadcast_debounced(
        self,
        session_id: str,
        message: dict[str, Any],
        debounce_key: str | None = None,
    ) -> None:
        """
        Broadcast message with debouncing to reduce excessive updates.

        Args:
            session_id: Session to broadcast to
            message: Message to broadcast
            debounce_key: Optional key for debouncing (defaults to session_id + message type)
        """
        if debounce_key is None:
            debounce_key = f"{session_id}_{message.get('type', 'unknown')}"

        # Directly call broadcast without debouncing (debouncer was removed)
        await self._do_broadcast(session_id, message)

    async def _do_broadcast(self, session_id: str, message: dict[str, Any]) -> None:
        """Internal method to perform the actual broadcast."""
        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]
        message_json = json.dumps(message)

        # Track performance
        time.time()

        # Send to all clients in session
        disconnected_clients = []
        for client in session.connected_clients:
            try:
                await client.send_text(message_json)
            except Exception:
                # Client disconnected, mark for removal
                disconnected_clients.append(client)

        # Clean up disconnected clients
        for client in disconnected_clients:
            session.remove_client(client)
            if client in self.client_sessions:
                del self.client_sessions[client]

        # Performance monitoring removed (external dependency)

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """
        Disconnect client from session.

        Args:
            websocket: WebSocket connection
            session_id: Session ID to leave
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.remove_client(websocket)

            # Clean up empty sessions
            if session.get_client_count() == 0:
                del self.sessions[session_id]

        if websocket in self.client_sessions:
            del self.client_sessions[websocket]

    async def handle_message(self, session_id: str, message: dict[str, Any]) -> None:
        """
        Handle incoming WebSocket message.

        Args:
            session_id: Session ID
            message: Message data
        """
        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]
        message_type = message.get("type")

        try:
            if message_type == "element_update":
                await self._handle_element_update(session, message)
            elif message_type == "connection_update":
                await self._handle_connection_update(session, message)
            elif message_type == "cursor_update":
                await self._handle_cursor_update(session, message)
            elif message_type == "selection_update":
                await self._handle_selection_update(session, message)
            elif message_type == "chat_message":
                await self._handle_chat_message(session, message)

        except Exception as e:
            # Send error back to client
            error_message = {
                "type": "error",
                "message": str(e),
                "original_message": message,
            }
            await self._send_to_session_clients(session, error_message)

    async def broadcast_to_session(
        self, session_id: str, message: dict[str, Any]
    ) -> None:
        """
        Broadcast message to all clients in session.

        Args:
            session_id: Session ID
            message: Message to broadcast
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            await self._send_to_session_clients(session, message)

    async def _send_current_state(
        self, websocket: WebSocket, session: DiagramSession
    ) -> None:
        """Send current diagram state to client."""
        state_message = {
            "type": "state_sync",
            "session_id": session.session_id,
            "diagram_type": session.builder.diagram_type.value,
            "elements": session.builder.to_dict()["elements"],
            "connections": session.builder.to_dict()["connections"],
            "metadata": session.builder.metadata,
            "client_count": session.get_client_count(),
        }

        await websocket.send_text(json.dumps(state_message))

    async def _broadcast_client_update(self, session_id: str) -> None:
        """Broadcast client count update to session."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            message = {
                "type": "client_update",
                "client_count": session.get_client_count(),
            }
            await self._send_to_session_clients(session, message)

    async def _send_to_session_clients(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """Send message to all clients in session."""
        if not session.connected_clients:
            return

        message_text = json.dumps(message)
        disconnected_clients = set()

        for client in session.connected_clients:
            try:
                await client.send_text(message_text)
            except Exception:
                # Client disconnected
                disconnected_clients.add(client)

        # Clean up disconnected clients
        for client in disconnected_clients:
            session.remove_client(client)
            if client in self.client_sessions:
                del self.client_sessions[client]

    async def _handle_element_update(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """Handle element update message."""
        element_id = message.get("element_id")
        updates = message.get("updates", {})

        if element_id and updates:
            # Apply updates to builder
            from .builder import Position, Size

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

            success = session.builder.update_element(element_id, **update_params)

            if success:
                # Broadcast update to other clients
                broadcast_message = {
                    "type": "element_updated",
                    "element_id": element_id,
                    "updates": updates,
                    "timestamp": datetime.now().isoformat(),
                }
                await self._send_to_session_clients(session, broadcast_message)

    async def _handle_connection_update(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> None:
        """Handle connection update message."""
        connection_id = message.get("connection_id")
        updates = message.get("updates", {})

        if connection_id and updates:
            # Apply updates to builder
            update_params: dict[str, Any] = {}
            if "label" in updates:
                update_params["label"] = updates["label"]
            if "connection_type" in updates:
                update_params["connection_type"] = updates["connection_type"]
            if "style" in updates:
                update_params["style"] = updates["style"]
            if "properties" in updates:
                update_params["properties"] = updates["properties"]

            success = session.builder.update_connection(connection_id, **update_params)

            if success:
                # Broadcast update to other clients
                broadcast_message = {
                    "type": "connection_updated",
                    "connection_id": connection_id,
                    "updates": updates,
                    "timestamp": datetime.now().isoformat(),
                }
                await self._send_to_session_clients(session, broadcast_message)

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
        await self._send_to_session_clients(session, cursor_data)

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
        await self._send_to_session_clients(session, selection_data)

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
        await self._send_to_session_clients(session, chat_data)

    def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """Get information about a session."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "client_count": session.get_client_count(),
            "diagram_type": session.builder.diagram_type.value,
            "element_count": len(session.builder.elements),
            "connection_count": len(session.builder.connections),
        }

    def get_all_sessions(self) -> list[dict[str, Any]]:
        """Get information about all active sessions."""
        # Filter out any None values to satisfy the return type.
        sessions: list[dict[str, Any]] = []
        for session_id in self.sessions.keys():
            info = self.get_session_info(session_id)
            if info is not None:
                sessions.append(info)
        return sessions
