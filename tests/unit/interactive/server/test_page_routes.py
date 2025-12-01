"""
Unit tests for interactive.server.page_routes module.

Tests the page routes setup.
"""

import tempfile
from pathlib import Path

import pytest
from unittest.mock import Mock

from diagramaid.interactive.server.page_routes import setup_page_routes


@pytest.mark.unit
class TestPageRoutes:
    """Unit tests for page routes."""

    def test_setup_page_routes(self) -> None:
        """Test setting up page routes."""
        mock_app = Mock()
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_dir = Path(tmpdir)
            # Create dummy template files
            (templates_dir / "index.html").write_text("<html></html>")
            (templates_dir / "builder.html").write_text("<html></html>")
            setup_page_routes(mock_app, templates_dir)
        # Should add routes to app
        assert mock_app.get.called

    def test_page_routes_added(self) -> None:
        """Test that page routes are added to app."""
        mock_app = Mock()
        mock_app.get = Mock(return_value=lambda f: f)
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_dir = Path(tmpdir)
            (templates_dir / "index.html").write_text("<html></html>")
            (templates_dir / "builder.html").write_text("<html></html>")
            setup_page_routes(mock_app, templates_dir)
        # Should have called app.get
        assert mock_app.get.called
