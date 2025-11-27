"""
Middleware configuration for the interactive diagram builder.

This module provides security and exception handling middleware.
"""

import logging
import traceback
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..security import SecurityValidator, api_rate_limiter


def setup_security_middleware(app: FastAPI) -> None:
    """
    Setup security middleware for rate limiting and origin validation.

    Args:
        app: FastAPI application
    """

    @app.middleware("http")  # type: ignore[misc]
    async def security_middleware(
        request: Request, call_next: Callable[..., Any]
    ) -> Any:
        """Security middleware for rate limiting and origin validation."""
        # Get client IP for rate limiting
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit for API endpoints
        if request.url.path.startswith("/api/"):
            if not api_rate_limiter.is_allowed(client_ip):
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": "Too many requests",
                    },
                )

        # Validate origin for sensitive endpoints
        origin = request.headers.get("origin")
        if request.method in [
            "POST",
            "PUT",
            "DELETE",
        ] and not SecurityValidator.validate_origin(origin):
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "message": "Invalid origin"},
            )

        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

    # Reference the middleware to avoid linter warnings
    _ = security_middleware


def setup_exception_handler(app: FastAPI) -> None:
    """
    Setup global exception handler.

    Args:
        app: FastAPI application
    """

    @app.exception_handler(Exception)  # type: ignore[misc]
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Global exception handler for better error reporting."""
        logging.error(f"Unhandled exception: {exc}")
        logging.error(traceback.format_exc())

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc),
                "type": type(exc).__name__,
            },
        )

    # Reference the handler to avoid linter warnings
    _ = global_exception_handler
