"""
WebSocket handler for real-time collaboration.

This module provides the main WebSocket handler that orchestrates
session management, message dispatching, and broadcasting.
"""

from typing import Any

from fastapi import WebSocket

from ..models import DiagramType
from ..security import InputSanitizer, SecurityValidator, websocket_rate_limiter
from .broadcast_service import BroadcastService
from .message_dispatcher import MessageDispatcher
from .session_manager import DiagramSession, SessionManager


class WebSocketHandler:
    """
    Handles WebSocket connections for real-time collaboration.

    Orchestrates session management, message dispatching, and
    broadcasting for collaborative diagram editing.
    """

    def __init__(self, max_sessions: int = 100) -> None:
        """
        Initialize WebSocket handler.

        Args:
            max_sessions: Maximum number of concurrent sessions
        """
        self._session_manager = SessionManager(max_sessions=max_sessions)
        self._broadcast_service = BroadcastService()
        self._message_dispatcher = MessageDispatcher(self._broadcast_service)

        # Client to session mapping
        self._client_sessions: dict[WebSocket, str] = {}

    @property
    def sessions(self) -> dict[str, DiagramSession]:
        """Get all active sessions."""
        return self._session_manager.sessions

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
            if not self._session_manager.has_session(session_id):
                from ..builder import DiagramBuilder

                builder = DiagramBuilder(DiagramType.FLOWCHART)
                self._session_manager.create_session(session_id, builder)

            # Add client to session
            session = self._session_manager.get_session(session_id)
            if session:
                session.add_client(websocket)
                self._client_sessions[websocket] = session_id

                # Send current state to new client
                await self._broadcast_service.send_state_sync(websocket, session)

                # Notify other clients about new connection
                await self._broadcast_service.send_client_count_update(session)

        except ValueError as e:
            # Invalid session ID or other validation error
            await websocket.close(code=1008, reason=str(e))
        except Exception:
            # Unexpected error during connection
            await websocket.close(code=1011, reason="Internal server error")

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """
        Disconnect client from session.

        Args:
            websocket: WebSocket connection
            session_id: Session ID to leave
        """
        self._session_manager.remove_client_from_session(session_id, websocket)

        # Clean up empty sessions
        session = self._session_manager.get_session(session_id)
        if session and session.is_empty():
            self._session_manager.remove_session(session_id)

        # Remove client mapping
        if websocket in self._client_sessions:
            del self._client_sessions[websocket]

    async def handle_message(
        self, session_id: str, message: dict[str, Any]
    ) -> None:
        """
        Handle incoming WebSocket message.

        Args:
            session_id: Session ID
            message: Message data
        """
        session = self._session_manager.get_session(session_id)
        if not session:
            return

        try:
            await self._message_dispatcher.dispatch(session, message)
        except Exception as e:
            # Send error back to clients
            error_message = {
                "type": "error",
                "message": str(e),
                "original_message": message,
            }
            await self._broadcast_service.send_to_session(session, error_message)

    async def broadcast_to_session(
        self, session_id: str, message: dict[str, Any]
    ) -> None:
        """
        Broadcast message to all clients in session.

        Args:
            session_id: Session ID
            message: Message to broadcast
        """
        session = self._session_manager.get_session(session_id)
        if session:
            disconnected = await self._broadcast_service.send_to_session(
                session, message
            )

            # Clean up disconnected clients
            for client in disconnected:
                session.remove_client(client)
                if client in self._client_sessions:
                    del self._client_sessions[client]

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
            debounce_key: Optional key for debouncing (unused, kept for compatibility)
        """
        session = self._session_manager.get_session(session_id)
        if session:
            await self._broadcast_service.broadcast_debounced(
                session_id, session, message
            )

    def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """Get information about a session."""
        return self._session_manager.get_session_info(session_id)

    def get_all_sessions(self) -> list[dict[str, Any]]:
        """Get information about all active sessions."""
        return self._session_manager.get_all_sessions_info()

    def get_client_session(self, websocket: WebSocket) -> str | None:
        """Get session ID for a client."""
        return self._client_sessions.get(websocket)
