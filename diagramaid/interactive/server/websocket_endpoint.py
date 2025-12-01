"""
WebSocket endpoint for the interactive diagram builder.

This module provides the WebSocket endpoint for real-time updates.
"""

import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from ..websocket import WebSocketHandler


def setup_websocket_endpoint(
    app: FastAPI, websocket_handler: WebSocketHandler
) -> None:
    """
    Setup WebSocket endpoint for real-time updates.

    Args:
        app: FastAPI application
        websocket_handler: WebSocket handler for managing connections
    """

    @app.websocket("/ws/{session_id}")  # type: ignore
    async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
        """WebSocket endpoint for real-time updates."""
        await websocket_handler.connect(websocket, session_id)

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                await websocket_handler.handle_message(session_id, message)

        except WebSocketDisconnect:
            websocket_handler.disconnect(websocket, session_id)

    # Reference the endpoint to avoid linter warnings
    _ = websocket_endpoint
