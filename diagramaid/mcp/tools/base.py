"""
Base utilities for MCP tools.

This module provides common utilities, error handling, and response formatting
used across all MCP tool implementations.
"""

import functools
import logging
import time
from typing import Any

try:
    from fastmcp import Context, FastMCP
    from pydantic import BaseModel, Field

    _FASTMCP_AVAILABLE = True
except ImportError:
    # Allow importing tools for testing without FastMCP
    FastMCP = None
    Context = None
    _FASTMCP_AVAILABLE = False

    # Create fallback classes for when pydantic is not available
    class BaseModel:  # type: ignore[no-redef]
        """Fallback BaseModel when pydantic is not available."""

        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(**kwargs: Any) -> Any:
        """Fallback Field when pydantic is not available."""
        return kwargs.get("default")


logger = logging.getLogger(__name__)


class ErrorCategory:
    """Error categories for better error classification."""

    VALIDATION = "ValidationError"
    RENDERING = "RenderingError"
    CONFIGURATION = "ConfigurationError"
    TEMPLATE = "TemplateError"
    FILE_OPERATION = "FileOperationError"
    AI_SERVICE = "AIServiceError"
    SYSTEM = "SystemError"
    NETWORK = "NetworkError"
    CACHE = "CacheError"


def create_success_response(
    data: Any,
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
    performance_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standardized success response."""
    import datetime

    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    if metadata:
        response["metadata"] = metadata

    if request_id:
        response["request_id"] = request_id

    if performance_metrics:
        response["performance"] = performance_metrics

    return response


def create_error_response(
    error: Exception,
    error_category: str = ErrorCategory.SYSTEM,
    context: dict[str, Any] | None = None,
    request_id: str | None = None,
    suggestions: list[str] | None = None,
) -> dict[str, Any]:
    """Create a standardized error response."""
    import datetime

    response = {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "error_category": error_category,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    if context:
        response["context"] = context

    if request_id:
        response["request_id"] = request_id

    if suggestions:
        response["suggestions"] = suggestions

    return response


def measure_performance(func: Any) -> Any:
    """Decorator to measure function performance."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()

            # Add performance metrics to successful responses
            if isinstance(result, dict) and result.get("success"):
                if "performance" not in result:
                    result["performance"] = {}
                result["performance"]["execution_time_ms"] = round(
                    (end_time - start_time) * 1000, 2
                )
                result["performance"]["function_name"] = func.__name__

            return result
        except Exception as e:
            end_time = time.time()
            # Add performance info to error context
            {
                "execution_time_ms": round((end_time - start_time) * 1000, 2),
                "function_name": func.__name__,
            }
            raise e

    return wrapper
