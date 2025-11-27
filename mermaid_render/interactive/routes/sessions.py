"""
Session management routes for the interactive diagram builder.

This module provides API endpoints for creating, retrieving,
and managing diagram editing sessions.
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from ..models import DiagramType
from ..security import InputSanitizer
from ..websocket import DiagramSession, WebSocketHandler


def create_sessions_router(
    sessions: dict[str, DiagramSession],
    websocket_handler: WebSocketHandler,
    max_sessions: int = 100,
) -> APIRouter:
    """
    Create the sessions router with the given dependencies.

    Args:
        sessions: Dictionary of active sessions
        websocket_handler: WebSocket handler for real-time updates
        max_sessions: Maximum number of concurrent sessions

    Returns:
        Configured APIRouter for session endpoints
    """
    router = APIRouter(prefix="/api/sessions", tags=["sessions"])

    @router.post("")
    async def create_session(diagram_type: str = "flowchart") -> dict[str, Any]:
        """Create new diagram session."""
        try:
            # Check resource limits
            if len(sessions) >= max_sessions:
                raise HTTPException(
                    status_code=503, detail="Maximum number of sessions reached"
                )

            # Import here to avoid circular imports
            from ..builder import DiagramBuilder

            session_id = str(uuid.uuid4())
            builder_obj: DiagramBuilder = DiagramBuilder(DiagramType(diagram_type))
            session = DiagramSession(session_id, builder_obj)

            sessions[session_id] = session

            return {
                "session_id": session_id,
                "diagram_type": diagram_type,
                "created_at": session.created_at.isoformat(),
            }
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid diagram type '{diagram_type}': {str(e)}",
            )
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Failed to create session: {e}")
            raise HTTPException(status_code=500, detail="Failed to create session")

    @router.get("/{session_id}")
    async def get_session(session_id: str) -> dict[str, Any]:
        """Get session information."""
        # Sanitize session ID
        try:
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]
        builder_state = session.builder.to_dict()
        return {
            "session_id": session_id,
            "diagram_type": session.builder.diagram_type.value,
            "elements": builder_state["elements"],
            "connections": builder_state["connections"],
            "metadata": session.builder.metadata,
        }

    @router.delete("/{session_id}")
    async def delete_session(session_id: str) -> dict[str, Any]:
        """Delete a diagram session."""
        # Sanitize session ID
        try:
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        del sessions[session_id]

        return {"success": True, "message": f"Session {session_id} deleted"}

    return router
