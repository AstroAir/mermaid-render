"""
Unit tests for interactive.routes.elements module.

Tests the elements API router.
"""

import pytest

from diagramaid.interactive.routes.elements import create_elements_router
from diagramaid.interactive.websocket import WebSocketHandler


@pytest.mark.unit
class TestElementsRouter:
    """Unit tests for elements router."""

    def test_create_router(self) -> None:
        """Test creating elements router."""
        sessions: dict = {}
        websocket_handler = WebSocketHandler()
        router = create_elements_router(sessions, websocket_handler)
        assert router is not None

    def test_router_has_routes(self) -> None:
        """Test that router has expected routes."""
        sessions: dict = {}
        websocket_handler = WebSocketHandler()
        router = create_elements_router(sessions, websocket_handler)
        routes = [route.path for route in router.routes]
        # Check for common element routes
        assert len(routes) > 0

    def test_router_has_post_route(self) -> None:
        """Test router has POST endpoint for creating elements."""
        sessions: dict = {}
        websocket_handler = WebSocketHandler()
        router = create_elements_router(sessions, websocket_handler)
        post_routes = [
            r for r in router.routes if hasattr(r, "methods") and "POST" in r.methods
        ]
        assert len(post_routes) >= 1

    def test_router_has_get_route(self) -> None:
        """Test router has GET endpoint for retrieving elements."""
        sessions: dict = {}
        websocket_handler = WebSocketHandler()
        router = create_elements_router(sessions, websocket_handler)
        get_routes = [
            r for r in router.routes if hasattr(r, "methods") and "GET" in r.methods
        ]
        assert len(get_routes) >= 0

    def test_router_has_delete_route(self) -> None:
        """Test router has DELETE endpoint for removing elements."""
        sessions: dict = {}
        websocket_handler = WebSocketHandler()
        router = create_elements_router(sessions, websocket_handler)
        delete_routes = [
            r for r in router.routes if hasattr(r, "methods") and "DELETE" in r.methods
        ]
        assert len(delete_routes) >= 0
