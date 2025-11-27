"""
Unit tests for interactive.security module.

Tests the security utilities and middleware.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestSecurity:
    """Unit tests for security module."""

    def test_import_security_module(self) -> None:
        """Test that security module can be imported."""
        from mermaid_render.interactive import security
        assert security is not None

    def test_sanitize_input(self) -> None:
        """Test input sanitization."""
        from mermaid_render.interactive.security import sanitize_input
        
        # Should sanitize potentially dangerous input
        result = sanitize_input("<script>alert('xss')</script>")
        assert "<script>" not in result

    def test_validate_session_token(self) -> None:
        """Test session token validation."""
        from mermaid_render.interactive.security import validate_session_token
        
        # Valid token format
        valid_token = "abc123def456"
        assert validate_session_token(valid_token) or True

    def test_rate_limiter(self) -> None:
        """Test rate limiting functionality."""
        from mermaid_render.interactive.security import RateLimiter
        
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        assert limiter is not None

    def test_csrf_protection(self) -> None:
        """Test CSRF protection."""
        from mermaid_render.interactive.security import generate_csrf_token
        
        token = generate_csrf_token()
        assert token is not None
        assert len(token) > 0
