"""
Unit tests for interactive.server.app_factory module.

Tests the FastAPI app factory.
"""

import pytest
from unittest.mock import Mock, patch

from diagramaid.interactive.server.app_factory import create_fastapi_app


@pytest.mark.unit
class TestAppFactory:
    """Unit tests for app factory."""

    def test_create_fastapi_app(self) -> None:
        """Test creating FastAPI app."""
        app = create_fastapi_app()
        assert app is not None

    def test_app_has_routes(self) -> None:
        """Test that app has routes."""
        app = create_fastapi_app()
        assert hasattr(app, 'routes')

    def test_app_title(self) -> None:
        """Test app title is set."""
        app = create_fastapi_app()
        assert app.title is not None

    def test_app_has_openapi(self) -> None:
        """Test that app has OpenAPI schema."""
        app = create_fastapi_app()
        assert hasattr(app, 'openapi')
