"""
Exception classes for the Mermaid Render library.

This module defines all custom exceptions used throughout the library,
providing clear error messages, error codes, suggestions for fixes,
and proper exception hierarchy.
"""

from typing import Any, Dict, List, Optional


class MermaidRenderError(Exception):
    """
    Base exception class for all Mermaid Render errors.

    All other exceptions in this library inherit from this base class,
    allowing for easy catching of any library-specific errors. Enhanced
    with error codes, suggestions, and structured error information.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Unique error code for programmatic handling
            suggestions: List of suggested fixes or workarounds
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.suggestions = suggestions or []
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]

        if self.error_code:
            parts.append(f"[{self.error_code}]")

        if self.suggestions:
            parts.append(f"Suggestions: {'; '.join(self.suggestions)}")

        if self.details:
            detail_str = ", ".join(f"{k}: {v}" for k, v in self.details.items())
            parts.append(f"Details: {detail_str}")

        return " - ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for structured error handling.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "suggestions": self.suggestions,
            "details": self.details
        }


class ValidationError(MermaidRenderError):
    """
    Raised when diagram validation fails.

    This exception is raised when:
    - Mermaid syntax is invalid
    - Diagram structure is malformed
    - Required elements are missing
    """

    def __init__(
        self,
        message: str,
        errors: Optional[List[str]] = None,
        line_number: Optional[int] = None,
        error_code: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            errors: List of specific validation errors
            line_number: Line number where error occurred (if applicable)
            error_code: Specific validation error code
            suggestions: List of suggested fixes
        """
        # Generate suggestions based on common validation errors
        auto_suggestions = self._generate_suggestions(message, errors or [])
        all_suggestions = (suggestions or []) + auto_suggestions

        super().__init__(
            message,
            error_code=error_code or "VALIDATION_ERROR",
            suggestions=all_suggestions
        )
        self.errors = errors or []
        self.line_number = line_number

    def _generate_suggestions(self, message: str, errors: List[str]) -> List[str]:
        """Generate automatic suggestions based on error patterns."""
        suggestions = []

        # Common validation error patterns and suggestions
        if "invalid diagram syntax" in message.lower():
            suggestions.append("Check the diagram type declaration (e.g., 'flowchart TD', 'sequenceDiagram')")
            suggestions.append("Verify that all nodes and connections use valid syntax")

        if "unmatched brackets" in message.lower() or any("bracket" in error.lower() for error in errors):
            suggestions.append("Check that all brackets are properly closed: [], (), {}")
            suggestions.append("Ensure node labels are properly enclosed in brackets")

        if "no nodes found" in message.lower():
            suggestions.append("Add at least one node to your diagram")
            suggestions.append("Check that node definitions follow the correct syntax")

        if "unknown diagram type" in message.lower():
            suggestions.append("Use a supported diagram type: flowchart, sequenceDiagram, classDiagram, etc.")
            suggestions.append("Check the spelling of your diagram type declaration")

        return suggestions

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.error_code:
            parts.append(f"[{self.error_code}]")

        if self.line_number:
            parts.append(f"Line {self.line_number}")

        if self.errors:
            parts.append(f"Errors: {', '.join(self.errors)}")

        if self.suggestions:
            parts.append(f"Suggestions: {'; '.join(self.suggestions)}")

        return " - ".join(parts)


class RenderingError(MermaidRenderError):
    """
    Raised when diagram rendering fails.

    This exception is raised when:
    - Network requests to rendering service fail
    - Output format conversion fails
    - File I/O operations fail during rendering
    """

    def __init__(
        self,
        message: str,
        format: Optional[str] = None,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize rendering error.

        Args:
            message: Error message
            format: Output format that failed
            status_code: HTTP status code (if applicable)
            error_code: Specific rendering error code
            suggestions: List of suggested fixes
        """
        # Generate suggestions based on common rendering errors
        auto_suggestions = self._generate_suggestions(message, format, status_code)
        all_suggestions = (suggestions or []) + auto_suggestions

        details = {}
        if format:
            details["format"] = format
        if status_code:
            details["status_code"] = status_code

        super().__init__(
            message,
            error_code=error_code or "RENDERING_ERROR",
            suggestions=all_suggestions,
            details=details
        )
        self.format = format
        self.status_code = status_code

    def _generate_suggestions(self, message: str, format: Optional[str], status_code: Optional[int]) -> List[str]:
        """Generate automatic suggestions based on error patterns."""
        suggestions = []

        # Network-related errors
        if status_code == 404:
            suggestions.append("Check if the rendering service URL is correct")
            suggestions.append("Verify that the service is running and accessible")
        elif status_code == 500:
            suggestions.append("The rendering service encountered an internal error")
            suggestions.append("Try again later or check the diagram syntax")
        elif status_code and status_code >= 400:
            suggestions.append("Check your network connection")
            suggestions.append("Verify the rendering service configuration")

        # Format-specific errors
        if format == "pdf" and "xml" in message.lower():
            suggestions.append("PDF rendering failed due to SVG parsing issues")
            suggestions.append("Try using SVG or PNG format instead")
            suggestions.append("Check if the diagram contains special characters")

        if "timeout" in message.lower():
            suggestions.append("Increase the timeout value in configuration")
            suggestions.append("Try rendering a simpler diagram first")

        if "file" in message.lower() and "permission" in message.lower():
            suggestions.append("Check file permissions for the output directory")
            suggestions.append("Ensure the output path is writable")

        return suggestions


class ConfigurationError(MermaidRenderError):
    """
    Raised when configuration is invalid or missing.

    This exception is raised when:
    - Required configuration values are missing
    - Configuration values are invalid
    - Theme configuration is malformed
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        expected_type: Optional[type] = None,
    ) -> None:
        """
        Initialize configuration error.

        Args:
            message: Error message
            config_key: Configuration key that caused the error
            expected_type: Expected type for the configuration value
        """
        super().__init__(message)
        self.config_key = config_key
        self.expected_type = expected_type

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.config_key:
            parts.append(f"Key: {self.config_key}")

        if self.expected_type:
            parts.append(f"Expected type: {self.expected_type.__name__}")

        return " - ".join(parts)


class UnsupportedFormatError(MermaidRenderError):
    """
    Raised when an unsupported output format is requested.

    This exception is raised when:
    - Requested format is not in the supported formats list
    - Format-specific features are not available
    """

    def __init__(
        self,
        message: str,
        requested_format: Optional[str] = None,
        supported_formats: Optional[List[str]] = None,
        error_code: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize unsupported format error.

        Args:
            message: Error message
            requested_format: The format that was requested
            supported_formats: List of supported formats
            error_code: Specific error code
            suggestions: List of suggested fixes
        """
        # Generate suggestions based on requested format
        auto_suggestions = self._generate_suggestions(requested_format, supported_formats or [])
        all_suggestions = (suggestions or []) + auto_suggestions

        details = {}
        if requested_format:
            details["requested_format"] = requested_format
        if supported_formats:
            details["supported_formats"] = supported_formats

        super().__init__(
            message,
            error_code=error_code or "UNSUPPORTED_FORMAT",
            suggestions=all_suggestions,
            details=details
        )
        self.requested_format = requested_format
        self.supported_formats = supported_formats or []

    def _generate_suggestions(self, requested_format: Optional[str], supported_formats: List[str]) -> List[str]:
        """Generate automatic suggestions based on requested format."""
        suggestions = []

        if requested_format and supported_formats:
            suggestions.append(f"Use one of the supported formats: {', '.join(supported_formats)}")

            # Suggest similar formats
            if requested_format.lower() in ["jpg", "jpeg"] and "png" in supported_formats:
                suggestions.append("Try 'png' format for raster images")
            elif requested_format.lower() == "html" and "svg" in supported_formats:
                suggestions.append("Try 'svg' format which can be embedded in HTML")
            elif requested_format.lower() in ["eps", "ps"] and "pdf" in supported_formats:
                suggestions.append("Try 'pdf' format for vector graphics")

        return suggestions


class DiagramError(MermaidRenderError):
    """
    Raised when there are issues with diagram construction or manipulation.

    This exception is raised when:
    - Invalid operations are performed on diagram objects
    - Diagram state is inconsistent
    - Required diagram elements are missing
    """

    def __init__(
        self,
        message: str,
        diagram_type: Optional[str] = None,
        operation: Optional[str] = None,
        error_code: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize diagram error.

        Args:
            message: Error message
            diagram_type: Type of diagram that caused the error
            operation: Operation that was being performed
            error_code: Specific error code
            suggestions: List of suggested fixes
        """
        auto_suggestions = self._generate_suggestions(message, diagram_type, operation)
        all_suggestions = (suggestions or []) + auto_suggestions

        details = {}
        if diagram_type:
            details["diagram_type"] = diagram_type
        if operation:
            details["operation"] = operation

        super().__init__(
            message,
            error_code=error_code or "DIAGRAM_ERROR",
            suggestions=all_suggestions,
            details=details
        )
        self.diagram_type = diagram_type
        self.operation = operation

    def _generate_suggestions(self, message: str, diagram_type: Optional[str], operation: Optional[str]) -> List[str]:
        """Generate automatic suggestions based on error context."""
        suggestions = []

        if "disposed" in message.lower():
            suggestions.append("Create a new diagram instance instead of reusing a disposed one")
            suggestions.append("Check that dispose() hasn't been called on this diagram")

        if operation == "add_node" and "duplicate" in message.lower():
            suggestions.append("Use unique node IDs for each node")
            suggestions.append("Check if the node already exists before adding")

        if operation == "add_edge" and "not found" in message.lower():
            suggestions.append("Ensure both source and target nodes exist before adding edges")
            suggestions.append("Check node ID spelling and case sensitivity")

        if diagram_type and "empty" in message.lower():
            suggestions.append(f"Add at least one element to your {diagram_type}")
            suggestions.append("Check the diagram construction methods for your diagram type")

        return suggestions


class ErrorAggregator:
    """
    Utility class for collecting and managing multiple errors.

    Useful for batch operations where multiple errors might occur
    and need to be reported together.
    """

    def __init__(self) -> None:
        """Initialize the error aggregator."""
        self.errors: List[MermaidRenderError] = []
        self.warnings: List[str] = []

    def add_error(self, error: MermaidRenderError) -> None:
        """Add an error to the collection."""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning to the collection."""
        self.warnings.append(warning)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors and warnings."""
        return {
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [error.to_dict() for error in self.errors],
            "warnings": self.warnings
        }

    def raise_if_errors(self, message: str = "Multiple errors occurred") -> None:
        """Raise an exception if there are any errors."""
        if self.has_errors():
            error_messages = [str(error) for error in self.errors]
            raise MermaidRenderError(
                message,
                error_code="MULTIPLE_ERRORS",
                details={
                    "error_count": len(self.errors),
                    "errors": error_messages,
                    "warnings": self.warnings
                }
            )


class NetworkError(RenderingError):
    """
    Raised when network operations fail.

    This exception is raised when:
    - Cannot connect to rendering service
    - Request timeout occurs
    - Network-related errors during rendering
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Initialize network error.

        Args:
            message: Error message
            url: URL that failed
            timeout: Timeout value that was exceeded
        """
        super().__init__(message)
        self.url = url
        self.timeout = timeout

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.url:
            parts.append(f"URL: {self.url}")

        if self.timeout:
            parts.append(f"Timeout: {self.timeout}s")

        return " - ".join(parts)


class ThemeError(ConfigurationError):
    """
    Raised when theme-related operations fail.

    This exception is raised when:
    - Theme does not exist
    - Theme configuration is invalid
    - Theme application fails
    """

    def __init__(
        self,
        message: str,
        theme_name: Optional[str] = None,
        available_themes: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize theme error.

        Args:
            message: Error message
            theme_name: Name of the theme that caused the error
            available_themes: List of available themes
        """
        super().__init__(message)
        self.theme_name = theme_name
        self.available_themes = available_themes or []

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.theme_name:
            parts.append(f"Theme: {self.theme_name}")

        if self.available_themes:
            parts.append(f"Available: {', '.join(self.available_themes)}")

        return " - ".join(parts)


class TemplateError(MermaidRenderError):
    """
    Raised when template-related operations fail.

    This exception is raised when:
    - Template does not exist
    - Template syntax is invalid
    - Template parameter validation fails
    - Template generation fails
    """

    def __init__(
        self,
        message: str,
        template_name: Optional[str] = None,
        parameter: Optional[str] = None,
    ) -> None:
        """
        Initialize template error.

        Args:
            message: Error message
            template_name: Name of the template that caused the error
            parameter: Specific parameter that caused the error
        """
        super().__init__(message)
        self.template_name = template_name
        self.parameter = parameter

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.template_name:
            parts.append(f"Template: {self.template_name}")

        if self.parameter:
            parts.append(f"Parameter: {self.parameter}")

        return " - ".join(parts)


class DataSourceError(MermaidRenderError):
    """
    Raised when data source operations fail.

    This exception is raised when:
    - Data source is not accessible
    - Data format is invalid
    - Data loading fails
    - Data transformation fails
    """

    def __init__(
        self,
        message: str,
        source_type: Optional[str] = None,
        source_location: Optional[str] = None,
    ) -> None:
        """
        Initialize data source error.

        Args:
            message: Error message
            source_type: Type of data source that caused the error
            source_location: Location/path of the data source
        """
        super().__init__(message)
        self.source_type = source_type
        self.source_location = source_location

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.source_type:
            parts.append(f"Source type: {self.source_type}")

        if self.source_location:
            parts.append(f"Location: {self.source_location}")

        return " - ".join(parts)


class CacheError(MermaidRenderError):
    """
    Raised when cache operations fail.

    This exception is raised when:
    - Cache backend is not accessible
    - Cache key operations fail
    - Cache serialization/deserialization fails
    - Cache storage limits are exceeded
    """

    def __init__(
        self,
        message: str,
        cache_backend: Optional[str] = None,
        cache_key: Optional[str] = None,
    ) -> None:
        """
        Initialize cache error.

        Args:
            message: Error message
            cache_backend: Type of cache backend that caused the error
            cache_key: Cache key that caused the error
        """
        super().__init__(message)
        self.cache_backend = cache_backend
        self.cache_key = cache_key

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.cache_backend:
            parts.append(f"Backend: {self.cache_backend}")

        if self.cache_key:
            parts.append(f"Key: {self.cache_key}")

        return " - ".join(parts)


class VersionControlError(MermaidRenderError):
    """
    Raised when version control operations fail.

    This exception is raised when:
    - Git operations fail
    - Branch operations fail
    - Merge conflicts cannot be resolved
    - Version history is corrupted
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> None:
        """
        Initialize version control error.

        Args:
            message: Error message
            operation: Version control operation that failed
            branch: Branch name that caused the error
        """
        super().__init__(message)
        self.operation = operation
        self.branch = branch

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.operation:
            parts.append(f"Operation: {self.operation}")

        if self.branch:
            parts.append(f"Branch: {self.branch}")

        return " - ".join(parts)
