"""
Session management for the interactive diagram builder.

This module provides session lifecycle management and client tracking.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from fastapi import WebSocket

if TYPE_CHECKING:
    from ..builder import DiagramBuilder


@dataclass
class DiagramSession:
    """Represents an active diagram editing session."""

    session_id: str
    builder: "DiagramBuilder"
    created_at: datetime
    updated_at: datetime
    connected_clients: set[WebSocket]

    def __init__(self, session_id: str, builder: "DiagramBuilder") -> None:
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

    def is_empty(self) -> bool:
        """Check if session has no connected clients."""
        return len(self.connected_clients) == 0

    def touch(self) -> None:
        """Update the session's last activity timestamp."""
        self.updated_at = datetime.now()


class SessionManager:
    """
    Manages diagram editing sessions.

    Handles session creation, retrieval, and cleanup.
    """

    def __init__(self, max_sessions: int = 100) -> None:
        """
        Initialize session manager.

        Args:
            max_sessions: Maximum number of concurrent sessions
        """
        self.sessions: dict[str, DiagramSession] = {}
        self.max_sessions = max_sessions

    def create_session(
        self, session_id: str, builder: "DiagramBuilder"
    ) -> DiagramSession:
        """
        Create a new session.

        Args:
            session_id: Unique session identifier
            builder: DiagramBuilder instance for this session

        Returns:
            Created DiagramSession
        """
        session = DiagramSession(session_id, builder)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> DiagramSession | None:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def has_session(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self.sessions

    def remove_session(self, session_id: str) -> bool:
        """
        Remove a session.

        Args:
            session_id: Session ID to remove

        Returns:
            True if session was removed
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def add_client_to_session(
        self, session_id: str, websocket: WebSocket
    ) -> bool:
        """
        Add a client to a session.

        Args:
            session_id: Session ID
            websocket: WebSocket connection

        Returns:
            True if client was added
        """
        session = self.sessions.get(session_id)
        if session:
            session.add_client(websocket)
            return True
        return False

    def remove_client_from_session(
        self, session_id: str, websocket: WebSocket
    ) -> bool:
        """
        Remove a client from a session.

        Args:
            session_id: Session ID
            websocket: WebSocket connection

        Returns:
            True if client was removed
        """
        session = self.sessions.get(session_id)
        if session:
            session.remove_client(websocket)
            return True
        return False

    def cleanup_empty_sessions(self) -> list[str]:
        """
        Remove all empty sessions.

        Returns:
            List of removed session IDs
        """
        empty_sessions = [
            sid for sid, session in self.sessions.items() if session.is_empty()
        ]
        for sid in empty_sessions:
            del self.sessions[sid]
        return empty_sessions

    def get_session_count(self) -> int:
        """Get total number of active sessions."""
        return len(self.sessions)

    def is_at_capacity(self) -> bool:
        """Check if session limit has been reached."""
        return len(self.sessions) >= self.max_sessions

    def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """Get information about a session."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "client_count": session.get_client_count(),
            "diagram_type": session.builder.diagram_type.value,
            "element_count": len(session.builder.elements),
            "connection_count": len(session.builder.connections),
        }

    def get_all_sessions_info(self) -> list[dict[str, Any]]:
        """Get information about all active sessions."""
        sessions_info: list[dict[str, Any]] = []
        for session_id in self.sessions:
            info = self.get_session_info(session_id)
            if info:
                sessions_info.append(info)
        return sessions_info
