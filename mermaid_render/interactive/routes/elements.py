"""
Element and connection routes for the interactive diagram builder.

This module provides API endpoints for managing diagram elements
and connections within editing sessions.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from ..models import ElementType, Position, Size
from ..security import InputSanitizer
from ..websocket import DiagramSession, WebSocketHandler


def create_elements_router(
    sessions: dict[str, DiagramSession],
    websocket_handler: WebSocketHandler,
) -> APIRouter:
    """
    Create the elements router with the given dependencies.

    Args:
        sessions: Dictionary of active sessions
        websocket_handler: WebSocket handler for real-time updates

    Returns:
        Configured APIRouter for element endpoints
    """
    router = APIRouter(prefix="/api/sessions", tags=["elements"])

    @router.post("/{session_id}/elements")
    async def add_element(
        session_id: str, element_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Add element to diagram."""
        try:
            # Sanitize session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)

            if session_id not in sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = sessions[session_id]

            # Sanitize and validate element data
            sanitized_data = InputSanitizer.sanitize_element_data(element_data)

            element = session.builder.add_element(
                element_type=ElementType(sanitized_data["element_type"]),
                label=sanitized_data["label"],
                position=Position.from_dict(sanitized_data["position"]),
                size=Size.from_dict(
                    sanitized_data.get("size", {"width": 120, "height": 60})
                ),
                properties=sanitized_data.get("properties", {}),
                style=sanitized_data.get("style", {}),
            )

            # Broadcast update to connected clients
            await websocket_handler.broadcast_to_session(
                session_id,
                {
                    "type": "element_added",
                    "element": element.to_dict(),
                },
            )

            return element.to_dict()

        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid element data: {str(e)}"
            )
        except KeyError as e:
            raise HTTPException(
                status_code=400, detail=f"Missing required field: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Failed to add element: {e}")
            raise HTTPException(status_code=500, detail="Failed to add element")

    @router.put("/{session_id}/elements/{element_id}")
    async def update_element(
        session_id: str, element_id: str, element_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update element in diagram."""
        try:
            # Sanitize session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        # Extract update parameters
        update_params: dict[str, Any] = {}
        if "label" in element_data:
            update_params["label"] = element_data["label"]
        if "position" in element_data:
            update_params["position"] = Position.from_dict(element_data["position"])
        if "size" in element_data:
            update_params["size"] = Size.from_dict(element_data["size"])
        if "properties" in element_data:
            update_params["properties"] = element_data["properties"]
        if "style" in element_data:
            update_params["style"] = element_data["style"]

        success = session.builder.update_element(element_id, **update_params)

        if not success:
            raise HTTPException(status_code=404, detail="Element not found")

        # Broadcast update to connected clients
        await websocket_handler.broadcast_to_session(
            session_id,
            {
                "type": "element_updated",
                "element_id": element_id,
                "updates": element_data,
            },
        )

        return {"success": True}

    @router.delete("/{session_id}/elements/{element_id}")
    async def remove_element(session_id: str, element_id: str) -> dict[str, Any]:
        """Remove element from diagram."""
        try:
            # Sanitize session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]
        success = session.builder.remove_element(element_id)

        if not success:
            raise HTTPException(status_code=404, detail="Element not found")

        # Broadcast update to connected clients
        await websocket_handler.broadcast_to_session(
            session_id,
            {
                "type": "element_removed",
                "element_id": element_id,
            },
        )

        return {"success": True}

    @router.post("/{session_id}/connections")
    async def add_connection(
        session_id: str, connection_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Add connection to diagram."""
        try:
            # Sanitize session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        connection = session.builder.add_connection(
            source_id=connection_data["source_id"],
            target_id=connection_data["target_id"],
            label=connection_data.get("label", ""),
            connection_type=connection_data.get("connection_type", "default"),
            style=connection_data.get("style", {}),
            properties=connection_data.get("properties", {}),
        )

        if not connection:
            raise HTTPException(status_code=400, detail="Invalid connection")

        # Broadcast update to connected clients
        await websocket_handler.broadcast_to_session(
            session_id,
            {
                "type": "connection_added",
                "connection": connection.to_dict(),
            },
        )

        return connection.to_dict()

    @router.put("/{session_id}/connections/{connection_id}")
    async def update_connection(
        session_id: str, connection_id: str, connection_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update connection in diagram."""
        try:
            # Sanitize session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        # Extract update parameters
        update_params: dict[str, Any] = {}
        if "label" in connection_data:
            update_params["label"] = connection_data["label"]
        if "connection_type" in connection_data:
            update_params["connection_type"] = connection_data["connection_type"]
        if "style" in connection_data:
            update_params["style"] = connection_data["style"]
        if "properties" in connection_data:
            update_params["properties"] = connection_data["properties"]

        success = session.builder.update_connection(connection_id, **update_params)

        if not success:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Broadcast update to connected clients
        await websocket_handler.broadcast_to_session(
            session_id,
            {
                "type": "connection_updated",
                "connection_id": connection_id,
                "updates": connection_data,
            },
        )

        return {"success": True}

    @router.delete("/{session_id}/connections/{connection_id}")
    async def remove_connection(session_id: str, connection_id: str) -> dict[str, Any]:
        """Remove connection from diagram."""
        try:
            # Sanitize session ID
            session_id = InputSanitizer.sanitize_session_id(session_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]
        success = session.builder.remove_connection(connection_id)

        if not success:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Broadcast update to connected clients
        await websocket_handler.broadcast_to_session(
            session_id,
            {
                "type": "connection_removed",
                "connection_id": connection_id,
            },
        )

        return {"success": True}

    return router
