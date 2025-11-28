"""
Unit tests for interactive.security module.

Tests the security utilities and middleware.
"""

import pytest

from mermaid_render.interactive.security import (
    InputSanitizer,
    RateLimitConfig,
    RateLimiter,
)


@pytest.mark.unit
class TestSecurity:
    """Unit tests for security module."""

    def test_import_security_module(self) -> None:
        """Test that security module can be imported."""
        from mermaid_render.interactive import security

        assert security is not None

    def test_sanitize_input(self) -> None:
        """Test input sanitization via InputSanitizer."""
        # Should raise for potentially dangerous input
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_label("<script>alert('xss')</script>")

    def test_sanitize_session_id(self) -> None:
        """Test session ID sanitization."""
        # Valid session ID
        valid_id = "abc123-def456"
        result = InputSanitizer.sanitize_session_id(valid_id)
        assert result == valid_id

    def test_rate_limiter(self) -> None:
        """Test rate limiting functionality."""
        config = RateLimitConfig(max_requests=10, window_seconds=60)
        limiter = RateLimiter(config)
        assert limiter is not None
        assert limiter.is_allowed("test_client")

    def test_rate_limiter_blocks_excess(self) -> None:
        """Test that rate limiter blocks excess requests."""
        config = RateLimitConfig(max_requests=2, window_seconds=60, burst_limit=10)
        limiter = RateLimiter(config)
        # First two requests should be allowed
        assert limiter.is_allowed("test_client")
        assert limiter.is_allowed("test_client")
        # Third should be blocked
        assert not limiter.is_allowed("test_client")
