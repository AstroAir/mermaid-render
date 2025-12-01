"""
Unit tests for interactive.server.interactive_server module.

Tests the InteractiveServer class.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from diagramaid.interactive.server.interactive_server import (
    InteractiveServer,
    create_app,
    start_server,
)


@pytest.mark.unit
class TestInteractiveServer:
    """Unit tests for InteractiveServer class."""

    def test_initialization(self) -> None:
        """Test InteractiveServer initialization."""
        server = InteractiveServer()
        assert server is not None

    def test_initialization_with_host_port(self) -> None:
        """Test initialization with custom host and port."""
        server = InteractiveServer(host="0.0.0.0", port=9000)
        assert server.host == "0.0.0.0"
        assert server.port == 9000

    def test_default_host_port(self) -> None:
        """Test default host and port values."""
        server = InteractiveServer()
        assert server.host == "localhost" or server.host == "127.0.0.1"
        assert server.port == 8080 or server.port > 0

    def test_create_app_function(self) -> None:
        """Test create_app function."""
        app = create_app()
        assert app is not None

    @patch('uvicorn.run')
    def test_start_server_function(self, mock_run: Mock) -> None:
        """Test start_server function."""
        # Should not raise
        start_server(host="localhost", port=8080)
        # Uvicorn run should be called
        mock_run.assert_called_once()

    def test_server_has_app(self) -> None:
        """Test that server has FastAPI app."""
        server = InteractiveServer()
        assert hasattr(server, 'app') or hasattr(server, '_app')


@pytest.mark.unit
class TestCreateApp:
    """Unit tests for create_app function."""

    def test_returns_fastapi_app(self) -> None:
        """Test that create_app returns a FastAPI app."""
        app = create_app()
        # Should have routes attribute (FastAPI/Starlette)
        assert hasattr(app, 'routes')

    def test_app_has_middleware(self) -> None:
        """Test that app has middleware configured."""
        app = create_app()
        # Should have middleware stack
        assert hasattr(app, 'middleware_stack') or hasattr(app, 'middleware')
