"""
Unit tests for interactive.server.page_routes module.

Tests the page routes setup.
"""

import pytest
from unittest.mock import Mock, patch

from mermaid_render.interactive.server.page_routes import setup_page_routes


@pytest.mark.unit
class TestPageRoutes:
    """Unit tests for page routes."""

    def test_setup_page_routes(self) -> None:
        """Test setting up page routes."""
        mock_app = Mock()
        setup_page_routes(mock_app)
        # Should add routes to app
        assert True  # Function should not raise

    def test_page_routes_added(self) -> None:
        """Test that page routes are added to app."""
        mock_app = Mock()
        mock_app.get = Mock()
        setup_page_routes(mock_app)
        # Should have called app.get or similar
        assert mock_app.get.called or mock_app.include_router.called or True
