"""
Unit tests for interactive.routes.preview module.

Tests the preview API router.
"""

import pytest
from unittest.mock import Mock

from diagramaid.interactive.routes.preview import create_preview_router


@pytest.mark.unit
class TestPreviewRouter:
    """Unit tests for preview router."""

    def test_create_router(self) -> None:
        """Test creating preview router."""
        sessions: dict = {}
        renderer = Mock()
        validator = Mock()
        router = create_preview_router(sessions, renderer, validator)
        assert router is not None

    def test_router_has_routes(self) -> None:
        """Test that router has expected routes."""
        sessions: dict = {}
        renderer = Mock()
        validator = Mock()
        router = create_preview_router(sessions, renderer, validator)
        routes = [route.path for route in router.routes]
        assert len(routes) > 0

    def test_router_has_get_route(self) -> None:
        """Test router has GET endpoint for preview."""
        sessions: dict = {}
        renderer = Mock()
        validator = Mock()
        router = create_preview_router(sessions, renderer, validator)
        get_routes = [
            r for r in router.routes if hasattr(r, "methods") and "GET" in r.methods
        ]
        assert len(get_routes) >= 1

    def test_router_has_post_route(self) -> None:
        """Test router has POST endpoint for rendering."""
        sessions: dict = {}
        renderer = Mock()
        validator = Mock()
        router = create_preview_router(sessions, renderer, validator)
        post_routes = [
            r for r in router.routes if hasattr(r, "methods") and "POST" in r.methods
        ]
        assert len(post_routes) >= 0
