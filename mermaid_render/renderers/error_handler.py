"""
Enhanced error handling for the Mermaid Render library.

This module provides comprehensive error handling, recovery strategies,
and detailed error reporting for the plugin-based rendering system.
"""

import logging
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from ..exceptions import RenderingError


class ErrorSeverity(Enum):
    """Error severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    NETWORK = "network"
    SYNTAX = "syntax"
    RENDERING = "rendering"
    SYSTEM = "system"
    TIMEOUT = "timeout"
    VALIDATION = "validation"


@dataclass
class ErrorContext:
    """Context information for an error."""
    
    renderer_name: Optional[str] = None
    format: Optional[str] = None
    diagram_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    input_size: Optional[int] = None
    attempt_number: int = 1
    total_attempts: int = 1
    elapsed_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorDetails:
    """Detailed error information."""
    
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    error_code: str
    context: ErrorContext
    original_exception: Optional[Exception] = None
    stack_trace: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    related_errors: List["ErrorDetails"] = field(default_factory=list)


class ErrorHandler:
    """
    Enhanced error handler for the rendering system.
    
    This class provides comprehensive error handling with categorization,
    severity assessment, recovery suggestions, and detailed reporting.
    """
    
    def __init__(self) -> None:
        """Initialize the error handler."""
        self.logger = logging.getLogger(__name__)
        self._error_patterns = self._initialize_error_patterns()
        self._recovery_strategies = self._initialize_recovery_strategies()
    
    def handle_error(
        self,
        exception: Exception,
        context: ErrorContext,
    ) -> ErrorDetails:
        """
        Handle and analyze an error.
        
        Args:
            exception: The exception that occurred
            context: Context information about the error
            
        Returns:
            ErrorDetails with comprehensive error information
        """
        # Classify the error
        category = self._classify_error(exception, context)
        severity = self._assess_severity(exception, category, context)
        error_code = self._generate_error_code(category, exception)
        
        # Get recovery suggestions
        recovery_suggestions = self._get_recovery_suggestions(
            exception, category, context
        )
        
        # Create error details
        error_details = ErrorDetails(
            message=str(exception),
            category=category,
            severity=severity,
            error_code=error_code,
            context=context,
            original_exception=exception,
            stack_trace=traceback.format_exc(),
            recovery_suggestions=recovery_suggestions,
        )
        
        # Log the error
        self._log_error(error_details)
        
        return error_details
    
    def _classify_error(
        self,
        exception: Exception,
        context: ErrorContext,
    ) -> ErrorCategory:
        """Classify an error into a category."""
        exception_type = type(exception).__name__
        message = str(exception).lower()
        
        # Check for specific patterns
        for pattern, category in self._error_patterns.items():
            if pattern in message or pattern in exception_type.lower():
                return category
        
        # Default classification based on exception type
        if "timeout" in exception_type.lower():
            return ErrorCategory.TIMEOUT
        elif "import" in exception_type.lower() or "module" in message:
            return ErrorCategory.DEPENDENCY
        elif "connection" in message or "network" in message:
            return ErrorCategory.NETWORK
        elif "config" in message or "setting" in message:
            return ErrorCategory.CONFIGURATION
        elif "syntax" in message or "parse" in message:
            return ErrorCategory.SYNTAX
        elif "render" in message:
            return ErrorCategory.RENDERING
        else:
            return ErrorCategory.SYSTEM
    
    def _assess_severity(
        self,
        exception: Exception,
        category: ErrorCategory,
        context: ErrorContext,
    ) -> ErrorSeverity:
        """Assess the severity of an error."""
        # Critical errors that prevent any rendering
        if category == ErrorCategory.DEPENDENCY and "playwright" in str(exception):
            return ErrorSeverity.MEDIUM  # Can fallback to other renderers
        
        if category == ErrorCategory.CONFIGURATION:
            return ErrorSeverity.HIGH
        
        if category == ErrorCategory.SYNTAX:
            return ErrorSeverity.HIGH
        
        if category == ErrorCategory.TIMEOUT:
            return ErrorSeverity.MEDIUM
        
        if category == ErrorCategory.NETWORK:
            return ErrorSeverity.MEDIUM  # Can fallback to local renderers
        
        # Consider attempt number
        if context.attempt_number >= context.total_attempts:
            return ErrorSeverity.HIGH  # Final attempt failed
        
        return ErrorSeverity.LOW
    
    def _generate_error_code(
        self,
        category: ErrorCategory,
        exception: Exception,
    ) -> str:
        """Generate a unique error code."""
        category_code = category.value.upper()[:4]
        exception_code = type(exception).__name__[:4].upper()
        return f"MR_{category_code}_{exception_code}"
    
    def _get_recovery_suggestions(
        self,
        exception: Exception,
        category: ErrorCategory,
        context: ErrorContext,
    ) -> List[str]:
        """Get recovery suggestions for an error."""
        suggestions = []
        message = str(exception).lower()
        
        # Category-specific suggestions
        if category == ErrorCategory.DEPENDENCY:
            if "playwright" in message:
                suggestions.extend([
                    "Install Playwright: pip install playwright",
                    "Install browser: playwright install chromium",
                    "Try using a different renderer (svg, png, pdf)",
                ])
            elif "graphviz" in message:
                suggestions.extend([
                    "Install Graphviz: pip install graphviz",
                    "Install Graphviz system binary from https://graphviz.org/download/",
                    "Use alternative renderers for flowcharts",
                ])
            elif "mmdc" in message or "node" in message:
                suggestions.extend([
                    "Install Node.js from https://nodejs.org/",
                    "Install Mermaid CLI: npm install -g @mermaid-js/mermaid-cli",
                    "Use alternative renderers (svg, playwright)",
                ])
        
        elif category == ErrorCategory.NETWORK:
            suggestions.extend([
                "Check internet connection",
                "Verify server URL is accessible",
                "Try using local renderers (playwright, nodejs)",
                "Check firewall settings",
            ])
        
        elif category == ErrorCategory.TIMEOUT:
            suggestions.extend([
                "Increase timeout value in configuration",
                "Simplify the diagram",
                "Try a different renderer",
                "Check system resources",
            ])
        
        elif category == ErrorCategory.SYNTAX:
            suggestions.extend([
                "Validate Mermaid syntax using online editor",
                "Check for unsupported diagram features",
                "Verify diagram type is supported by the renderer",
                "Try a different renderer that supports more features",
            ])
        
        elif category == ErrorCategory.CONFIGURATION:
            suggestions.extend([
                "Check configuration values are valid",
                "Verify required configuration keys are present",
                "Reset to default configuration",
                "Check configuration schema documentation",
            ])
        
        # Renderer-specific suggestions
        if context.renderer_name:
            renderer_suggestions = self._recovery_strategies.get(context.renderer_name, [])
            suggestions.extend(renderer_suggestions)
        
        return suggestions
    
    def _initialize_error_patterns(self) -> Dict[str, ErrorCategory]:
        """Initialize error pattern mappings."""
        return {
            "timeout": ErrorCategory.TIMEOUT,
            "connection": ErrorCategory.NETWORK,
            "network": ErrorCategory.NETWORK,
            "dns": ErrorCategory.NETWORK,
            "ssl": ErrorCategory.NETWORK,
            "certificate": ErrorCategory.NETWORK,
            "import": ErrorCategory.DEPENDENCY,
            "module": ErrorCategory.DEPENDENCY,
            "not found": ErrorCategory.DEPENDENCY,
            "syntax": ErrorCategory.SYNTAX,
            "parse": ErrorCategory.SYNTAX,
            "invalid": ErrorCategory.SYNTAX,
            "config": ErrorCategory.CONFIGURATION,
            "setting": ErrorCategory.CONFIGURATION,
            "permission": ErrorCategory.SYSTEM,
            "access": ErrorCategory.SYSTEM,
            "memory": ErrorCategory.SYSTEM,
            "disk": ErrorCategory.SYSTEM,
        }
    
    def _initialize_recovery_strategies(self) -> Dict[str, List[str]]:
        """Initialize renderer-specific recovery strategies."""
        return {
            "svg": [
                "Check mermaid.ink service status",
                "Verify internet connectivity",
                "Try local rendering with playwright or nodejs",
            ],
            "png": [
                "Check mermaid.ink service status",
                "Verify image dimensions are reasonable",
                "Try SVG format first, then convert locally",
            ],
            "pdf": [
                "Ensure cairosvg is installed",
                "Check SVG renderer is working",
                "Try alternative PDF conversion tools",
            ],
            "playwright": [
                "Ensure Playwright browsers are installed",
                "Check browser launch permissions",
                "Try different browser type (chromium, firefox, webkit)",
                "Increase timeout values",
            ],
            "nodejs": [
                "Install Node.js and Mermaid CLI",
                "Check mmdc command is in PATH",
                "Verify Node.js version compatibility",
                "Try alternative local renderers",
            ],
            "graphviz": [
                "Install Graphviz system binary",
                "Check if diagram type is supported (flowcharts only)",
                "Try alternative renderers for unsupported diagram types",
            ],
        }
    
    def _log_error(self, error_details: ErrorDetails) -> None:
        """Log error details with appropriate level."""
        log_message = (
            f"[{error_details.error_code}] {error_details.message} "
            f"(Category: {error_details.category.value}, "
            f"Severity: {error_details.severity.value})"
        )
        
        if error_details.context.renderer_name:
            log_message += f" [Renderer: {error_details.context.renderer_name}]"
        
        # Log with appropriate level based on severity
        if error_details.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_details.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_details.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Log recovery suggestions at debug level
        if error_details.recovery_suggestions:
            self.logger.debug(
                f"Recovery suggestions for {error_details.error_code}: "
                f"{'; '.join(error_details.recovery_suggestions)}"
            )
    
    def format_error_report(self, error_details: ErrorDetails) -> str:
        """Format a comprehensive error report."""
        report_lines = [
            f"Error Report - {error_details.error_code}",
            "=" * 50,
            f"Message: {error_details.message}",
            f"Category: {error_details.category.value}",
            f"Severity: {error_details.severity.value}",
            "",
            "Context:",
        ]
        
        # Add context information
        if error_details.context.renderer_name:
            report_lines.append(f"  Renderer: {error_details.context.renderer_name}")
        if error_details.context.format:
            report_lines.append(f"  Format: {error_details.context.format}")
        if error_details.context.diagram_type:
            report_lines.append(f"  Diagram Type: {error_details.context.diagram_type}")
        if error_details.context.attempt_number > 1:
            report_lines.append(
                f"  Attempt: {error_details.context.attempt_number}/"
                f"{error_details.context.total_attempts}"
            )
        if error_details.context.elapsed_time > 0:
            report_lines.append(f"  Elapsed Time: {error_details.context.elapsed_time:.2f}s")
        
        # Add recovery suggestions
        if error_details.recovery_suggestions:
            report_lines.extend([
                "",
                "Recovery Suggestions:",
            ])
            for i, suggestion in enumerate(error_details.recovery_suggestions, 1):
                report_lines.append(f"  {i}. {suggestion}")
        
        return "\n".join(report_lines)


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_global_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler
