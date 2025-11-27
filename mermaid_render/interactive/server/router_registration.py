"""
Router registration for the interactive diagram builder.

This module provides functions to register API routers.
"""

from fastapi import FastAPI

from ...core import MermaidRenderer
from ...validators.validator import MermaidValidator
from ..routes import (
    create_elements_router,
    create_preview_router,
    create_sessions_router,
)
from ..websocket import DiagramSession, WebSocketHandler


def register_api_routers(
    app: FastAPI,
    sessions: dict[str, DiagramSession],
    websocket_handler: WebSocketHandler,
    renderer: MermaidRenderer,
    validator: MermaidValidator,
    max_sessions: int = 100,
) -> None:
    """
    Register all API routers.

    Args:
        app: FastAPI application
        sessions: Dictionary of active sessions
        websocket_handler: WebSocket handler for real-time updates
        renderer: MermaidRenderer instance for rendering diagrams
        validator: MermaidValidator instance for code validation
        max_sessions: Maximum number of concurrent sessions
    """
    # Create and register session routes
    sessions_router = create_sessions_router(
        sessions=sessions,
        websocket_handler=websocket_handler,
        max_sessions=max_sessions,
    )
    app.include_router(sessions_router)

    # Create and register element routes
    elements_router = create_elements_router(
        sessions=sessions,
        websocket_handler=websocket_handler,
    )
    app.include_router(elements_router)

    # Create and register preview routes
    preview_router = create_preview_router(
        sessions=sessions,
        renderer=renderer,
        validator=validator,
    )
    app.include_router(preview_router)
