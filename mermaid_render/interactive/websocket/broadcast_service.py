"""
Broadcast service for the interactive diagram builder.

This module provides message broadcasting functionality for WebSocket clients.
"""

import asyncio
import json
import time
from typing import Any

from fastapi import WebSocket

from .session_manager import DiagramSession


class BroadcastService:
    """
    Handles message broadcasting to WebSocket clients.

    Provides methods for sending messages to individual clients,
    sessions, and with debouncing support.
    """

    def __init__(self, debounce_delay: float = 0.1) -> None:
        """
        Initialize broadcast service.

        Args:
            debounce_delay: Delay in seconds for debounced broadcasts
        """
        self.debounce_delay = debounce_delay
        self._pending_broadcasts: dict[str, dict[str, Any]] = {}
        self._last_broadcast_time: dict[str, float] = {}

    async def send_to_client(
        self, websocket: WebSocket, message: dict[str, Any]
    ) -> bool:
        """
        Send message to a single client.

        Args:
            websocket: WebSocket connection
            message: Message to send

        Returns:
            True if message was sent successfully
        """
        try:
            await websocket.send_text(json.dumps(message))
            return True
        except Exception:
            return False

    async def send_to_session(
        self, session: DiagramSession, message: dict[str, Any]
    ) -> set[WebSocket]:
        """
        Send message to all clients in a session.

        Args:
            session: DiagramSession to broadcast to
            message: Message to send

        Returns:
            Set of disconnected clients
        """
        if not session.connected_clients:
            return set()

        message_text = json.dumps(message)
        disconnected_clients: set[WebSocket] = set()

        for client in session.connected_clients:
            try:
                await client.send_text(message_text)
            except Exception:
                disconnected_clients.add(client)

        return disconnected_clients

    async def broadcast_to_session(
        self,
        session: DiagramSession,
        message: dict[str, Any],
        exclude: WebSocket | None = None,
    ) -> set[WebSocket]:
        """
        Broadcast message to all clients in a session, optionally excluding one.

        Args:
            session: DiagramSession to broadcast to
            message: Message to send
            exclude: Optional client to exclude from broadcast

        Returns:
            Set of disconnected clients
        """
        if not session.connected_clients:
            return set()

        message_text = json.dumps(message)
        disconnected_clients: set[WebSocket] = set()

        for client in session.connected_clients:
            if client == exclude:
                continue
            try:
                await client.send_text(message_text)
            except Exception:
                disconnected_clients.add(client)

        return disconnected_clients

    async def broadcast_debounced(
        self,
        session_id: str,
        session: DiagramSession,
        message: dict[str, Any],
    ) -> None:
        """
        Broadcast message with debouncing to reduce update frequency.

        Args:
            session_id: Session identifier for debounce tracking
            session: DiagramSession to broadcast to
            message: Message to send
        """
        current_time = time.time()
        last_time = self._last_broadcast_time.get(session_id, 0)

        # Store pending message
        self._pending_broadcasts[session_id] = message

        # If enough time has passed, send immediately
        if current_time - last_time >= self.debounce_delay:
            await self._send_pending_broadcast(session_id, session)
        else:
            # Schedule delayed broadcast
            delay = self.debounce_delay - (current_time - last_time)
            asyncio.create_task(
                self._delayed_broadcast(session_id, session, delay)
            )

    async def _delayed_broadcast(
        self, session_id: str, session: DiagramSession, delay: float
    ) -> None:
        """Send a delayed broadcast after the specified delay."""
        await asyncio.sleep(delay)
        await self._send_pending_broadcast(session_id, session)

    async def _send_pending_broadcast(
        self, session_id: str, session: DiagramSession
    ) -> None:
        """Send pending broadcast for a session."""
        message = self._pending_broadcasts.pop(session_id, None)
        if message:
            self._last_broadcast_time[session_id] = time.time()
            disconnected = await self.send_to_session(session, message)

            # Clean up disconnected clients
            for client in disconnected:
                session.remove_client(client)

    async def send_state_sync(
        self, websocket: WebSocket, session: DiagramSession
    ) -> bool:
        """
        Send current diagram state to a client.

        Args:
            websocket: WebSocket connection
            session: DiagramSession containing state

        Returns:
            True if state was sent successfully
        """
        state_message = {
            "type": "state_sync",
            "session_id": session.session_id,
            "diagram_type": session.builder.diagram_type.value,
            "elements": session.builder.to_dict()["elements"],
            "connections": session.builder.to_dict()["connections"],
            "metadata": session.builder.metadata,
            "client_count": session.get_client_count(),
        }
        return await self.send_to_client(websocket, state_message)

    async def send_client_count_update(
        self, session: DiagramSession
    ) -> set[WebSocket]:
        """
        Broadcast client count update to all clients in session.

        Args:
            session: DiagramSession to broadcast to

        Returns:
            Set of disconnected clients
        """
        message = {
            "type": "client_update",
            "client_count": session.get_client_count(),
        }
        return await self.send_to_session(session, message)

    async def send_error(
        self, websocket: WebSocket, error_message: str, error_code: str = "error"
    ) -> bool:
        """
        Send error message to a client.

        Args:
            websocket: WebSocket connection
            error_message: Error description
            error_code: Error code/type

        Returns:
            True if error was sent successfully
        """
        message = {
            "type": "error",
            "code": error_code,
            "message": error_message,
        }
        return await self.send_to_client(websocket, message)
