"""
Exception classes for the Mermaid Render library.

This module defines all custom exceptions used throughout the library,
providing clear error messages and proper exception hierarchy.
"""

from typing import Any, List, Optional


class MermaidRenderError(Exception):
    """
    Base exception class for all Mermaid Render errors.

    All other exceptions in this library inherit from this base class,
    allowing for easy catching of any library-specific errors.
    """

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


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
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            errors: List of specific validation errors
            line_number: Line number where error occurred (if applicable)
        """
        super().__init__(message)
        self.errors = errors or []
        self.line_number = line_number

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.line_number:
            parts.append(f"Line {self.line_number}")

        if self.errors:
            parts.append(f"Errors: {', '.join(self.errors)}")

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
    ) -> None:
        """
        Initialize rendering error.

        Args:
            message: Error message
            format: Output format that failed
            status_code: HTTP status code (if applicable)
        """
        super().__init__(message)
        self.format = format
        self.status_code = status_code

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.format:
            parts.append(f"Format: {self.format}")

        if self.status_code:
            parts.append(f"Status: {self.status_code}")

        return " - ".join(parts)


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
    ) -> None:
        """
        Initialize unsupported format error.

        Args:
            message: Error message
            requested_format: The format that was requested
            supported_formats: List of supported formats
        """
        super().__init__(message)
        self.requested_format = requested_format
        self.supported_formats = supported_formats or []

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.requested_format:
            parts.append(f"Requested: {self.requested_format}")

        if self.supported_formats:
            parts.append(f"Supported: {', '.join(self.supported_formats)}")

        return " - ".join(parts)


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


class DiagramError(MermaidRenderError):
    """
    Raised when diagram-specific operations fail.

    This exception is raised when:
    - Diagram construction fails
    - Invalid diagram elements are added
    - Diagram state is inconsistent
    """

    def __init__(
        self,
        message: str,
        diagram_type: Optional[str] = None,
        element: Optional[str] = None,
    ) -> None:
        """
        Initialize diagram error.

        Args:
            message: Error message
            diagram_type: Type of diagram that caused the error
            element: Specific diagram element that caused the error
        """
        super().__init__(message)
        self.diagram_type = diagram_type
        self.element = element

    def __str__(self) -> str:
        """Return detailed error message."""
        parts = [self.message]

        if self.diagram_type:
            parts.append(f"Diagram type: {self.diagram_type}")

        if self.element:
            parts.append(f"Element: {self.element}")

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
