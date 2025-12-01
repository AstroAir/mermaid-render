"""
Unit tests for mcp.tools.base module.

Tests for error categories, response creation, and performance measurement.
"""

import pytest

from diagramaid.mcp.tools.base import (
    ErrorCategory,
    create_error_response,
    create_success_response,
    measure_performance,
)


@pytest.mark.unit
class TestErrorCategory:
    """Tests for ErrorCategory enum."""

    def test_error_categories_exist(self):
        """Test that all expected error categories exist."""
        assert hasattr(ErrorCategory, "VALIDATION")
        assert hasattr(ErrorCategory, "RENDERING")
        assert hasattr(ErrorCategory, "CONFIGURATION")
        assert hasattr(ErrorCategory, "TEMPLATE")
        assert hasattr(ErrorCategory, "FILE_OPERATION")
        assert hasattr(ErrorCategory, "CACHE")
        assert hasattr(ErrorCategory, "SYSTEM")

    def test_error_category_values(self):
        """Test error category values are strings."""
        assert isinstance(ErrorCategory.VALIDATION, str)
        assert isinstance(ErrorCategory.RENDERING, str)


@pytest.mark.unit
class TestCreateSuccessResponse:
    """Tests for create_success_response function."""

    def test_success_response_structure(self):
        """Test success response has correct structure."""
        response = create_success_response(data={"key": "value"})

        assert response["success"] is True
        assert "data" in response
        assert response["data"]["key"] == "value"

    def test_success_response_with_metadata(self):
        """Test success response includes metadata."""
        response = create_success_response(
            data={"key": "value"}, metadata={"extra": "info"}
        )

        assert response["success"] is True
        assert "metadata" in response
        assert response["metadata"]["extra"] == "info"

    def test_success_response_with_empty_data(self):
        """Test success response can be created with empty data."""
        response = create_success_response(data={})

        assert response["success"] is True


@pytest.mark.unit
class TestCreateErrorResponse:
    """Tests for create_error_response function."""

    def test_error_response_structure(self):
        """Test error response has correct structure."""
        error = ValueError("Test error")
        response = create_error_response(error, ErrorCategory.VALIDATION)

        assert response["success"] is False
        assert "error" in response
        assert "error_type" in response

    def test_error_response_with_context(self):
        """Test error response includes context."""
        error = ValueError("Test error")
        response = create_error_response(
            error, ErrorCategory.VALIDATION, context={"field": "test"}
        )

        assert response["success"] is False
        assert "context" in response
        assert response["context"]["field"] == "test"

    def test_error_response_with_suggestions(self):
        """Test error response includes suggestions."""
        error = ValueError("Test error")
        response = create_error_response(
            error, ErrorCategory.VALIDATION, suggestions=["Try this", "Or that"]
        )

        assert response["success"] is False
        assert "suggestions" in response
        assert len(response["suggestions"]) == 2


@pytest.mark.unit
class TestMeasurePerformance:
    """Tests for measure_performance decorator."""

    def test_decorator_preserves_function_result(self):
        """Test decorator returns original function result."""

        @measure_performance
        def sample_function():
            return {"success": True, "data": "test"}

        result = sample_function()
        assert result["success"] is True
        assert result["data"] == "test"

    def test_decorator_adds_performance_metadata(self):
        """Test decorator adds performance metadata."""

        @measure_performance
        def sample_function():
            return {"success": True, "data": "test"}

        result = sample_function()
        # Performance metadata should be added at top level
        assert "performance" in result

    def test_decorator_handles_non_dict_return(self):
        """Test decorator handles non-dict return values."""

        @measure_performance
        def sample_function():
            return "string result"

        result = sample_function()
        assert result == "string result"
