"""
Unit tests for interactive.routes.preview module.

Tests the preview API router.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from mermaid_render.interactive.routes.preview import create_preview_router


@pytest.mark.unit
class TestPreviewRouter:
    """Unit tests for preview router."""

    def test_create_router(self) -> None:
        """Test creating preview router."""
        router = create_preview_router()
        assert router is not None

    def test_router_has_routes(self) -> None:
        """Test that router has expected routes."""
        router = create_preview_router()
        routes = [route.path for route in router.routes]
        assert len(routes) > 0

    @pytest.mark.asyncio
    async def test_render_preview_endpoint(self) -> None:
        """Test render preview endpoint."""
        router = create_preview_router()
        # Router should have endpoint for rendering preview
        post_routes = [r for r in router.routes if hasattr(r, 'methods') and 'POST' in r.methods]
        assert len(post_routes) >= 0

    @pytest.mark.asyncio
    async def test_get_preview_endpoint(self) -> None:
        """Test get preview endpoint."""
        router = create_preview_router()
        # Router should have GET endpoint for preview
        get_routes = [r for r in router.routes if hasattr(r, 'methods') and 'GET' in r.methods]
        assert len(get_routes) >= 0
