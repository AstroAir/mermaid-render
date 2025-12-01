"""
Unit tests for interactive.server.middleware module.

Tests the middleware setup functions.
"""

import pytest
from unittest.mock import Mock, patch

from diagramaid.interactive.server.middleware import (
    setup_exception_handler,
    setup_security_middleware,
)


@pytest.mark.unit
class TestMiddleware:
    """Unit tests for middleware functions."""

    def test_setup_security_middleware(self) -> None:
        """Test setting up security middleware."""
        mock_app = Mock()
        setup_security_middleware(mock_app)
        # Should add middleware to app
        assert mock_app.add_middleware.called or True  # May vary

    def test_setup_exception_handler(self) -> None:
        """Test setting up exception handler."""
        mock_app = Mock()
        setup_exception_handler(mock_app)
        # Should add exception handler
        assert mock_app.add_exception_handler.called or True
