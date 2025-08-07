"""
Live validation for interactive diagram building.

This module provides real-time validation capabilities for diagrams
being built in the interactive interface.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..validators import MermaidValidator


@dataclass
class ValidationIssue:
    """Represents a validation issue with position information."""

    type: str  # error, warning, info
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    element_id: Optional[str] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "element_id": self.element_id,
            "suggestion": self.suggestion,
        }


@dataclass
class ValidationResult:
    """Enhanced validation result for interactive use."""

    is_valid: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    suggestions: List[ValidationIssue]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "suggestions": [s.to_dict() for s in self.suggestions],
        }


class LiveValidator:
    """
    Live validator for interactive diagram building.

    Provides real-time validation with enhanced feedback for
    interactive diagram construction.
    """

    def __init__(self):
        """Initialize live validator."""
        self.base_validator = MermaidValidator()

        # Interactive-specific validation rules
        self.interactive_rules = {
            "min_elements": 1,
            "max_elements": 100,
            "min_connections": 0,
            "max_connections": 200,
            "max_label_length": 100,
        }

    def validate(self, diagram_code: str) -> ValidationResult:
        """
        Validate diagram code with enhanced feedback.

        Args:
            diagram_code: Mermaid diagram code to validate

        Returns:
            Enhanced validation result
        """
        errors = []
        warnings = []
        suggestions = []

        # Basic syntax validation
        base_result = self.base_validator.validate(diagram_code)

        # Convert base validation results
        for error in base_result.errors:
            errors.append(
                ValidationIssue(
                    type="error",
                    message=error,
                    suggestion=self._get_error_suggestion(error),
                )
            )

        for warning in base_result.warnings:
            warnings.append(
                ValidationIssue(
                    type="warning",
                    message=warning,
                    suggestion=self._get_warning_suggestion(warning),
                )
            )

        # Interactive-specific validation
        interactive_issues = self._validate_interactive_rules(diagram_code)
        errors.extend(interactive_issues["errors"])
        warnings.extend(interactive_issues["warnings"])
        suggestions.extend(interactive_issues["suggestions"])

        # Performance suggestions
        performance_suggestions = self._get_performance_suggestions(diagram_code)
        suggestions.extend(performance_suggestions)

        # Accessibility suggestions
        accessibility_suggestions = self._get_accessibility_suggestions(diagram_code)
        suggestions.extend(accessibility_suggestions)

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
        )

    def validate_element(self, element_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate individual element.

        Args:
            element_data: Element data to validate

        Returns:
            Validation result for element
        """
        errors = []
        warnings = []
        suggestions = []

        # Validate label
        label = element_data.get("label", "")
        if not label.strip():
            errors.append(
                ValidationIssue(
                    type="error",
                    message="Element label cannot be empty",
                    element_id=element_data.get("id"),
                    suggestion="Add a descriptive label for the element",
                )
            )
        elif len(label) > self.interactive_rules["max_label_length"]:
            warnings.append(
                ValidationIssue(
                    type="warning",
                    message=f"Label is very long ({len(label)} characters)",
                    element_id=element_data.get("id"),
                    suggestion="Consider using a shorter, more concise label",
                )
            )

        # Validate position
        position = element_data.get("position", {})
        if position.get("x", 0) < 0 or position.get("y", 0) < 0:
            warnings.append(
                ValidationIssue(
                    type="warning",
                    message="Element position is outside visible area",
                    element_id=element_data.get("id"),
                    suggestion="Move element to positive coordinates",
                )
            )

        # Validate size
        size = element_data.get("size", {})
        if size.get("width", 0) < 10 or size.get("height", 0) < 10:
            warnings.append(
                ValidationIssue(
                    type="warning",
                    message="Element size is very small",
                    element_id=element_data.get("id"),
                    suggestion="Increase element size for better visibility",
                )
            )

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
        )

    def validate_connection(
        self, connection_data: Dict[str, Any], elements: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate connection between elements.

        Args:
            connection_data: Connection data to validate
            elements: Available elements

        Returns:
            Validation result for connection
        """
        errors = []
        warnings = []
        suggestions = []

        source_id = connection_data.get("source_id")
        target_id = connection_data.get("target_id")

        # Validate source and target exist
        if source_id not in elements:
            errors.append(
                ValidationIssue(
                    type="error",
                    message=f"Source element '{source_id}' not found",
                    suggestion="Select a valid source element",
                )
            )

        if target_id not in elements:
            errors.append(
                ValidationIssue(
                    type="error",
                    message=f"Target element '{target_id}' not found",
                    suggestion="Select a valid target element",
                )
            )

        # Validate self-connection
        if source_id == target_id:
            warnings.append(
                ValidationIssue(
                    type="warning",
                    message="Element is connected to itself",
                    suggestion="Consider if self-connection is intentional",
                )
            )

        # Validate label length
        label = connection_data.get("label", "")
        if len(label) > 50:
            warnings.append(
                ValidationIssue(
                    type="warning",
                    message="Connection label is very long",
                    suggestion="Use a shorter label for better readability",
                )
            )

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
        )

    def _validate_interactive_rules(
        self, diagram_code: str
    ) -> Dict[str, List[ValidationIssue]]:
        """Validate interactive-specific rules."""
        errors = []
        warnings = []
        suggestions = []

        lines = diagram_code.strip().split("\n")

        # Count elements and connections
        element_count = 0
        connection_count = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith("%"):
                continue

            # Count elements (simplified)
            if "[" in line and "]" in line:
                element_count += 1

            # Count connections (simplified)
            if "-->" in line or "---" in line:
                connection_count += 1

        # Validate element count
        if element_count < self.interactive_rules["min_elements"]:
            warnings.append(
                ValidationIssue(
                    type="warning",
                    message="Diagram has very few elements",
                    suggestion="Add more elements to create a meaningful diagram",
                )
            )
        elif element_count > self.interactive_rules["max_elements"]:
            warnings.append(
                ValidationIssue(
                    type="warning",
                    message=f"Diagram has many elements ({element_count})",
                    suggestion="Consider breaking into smaller diagrams",
                )
            )

        # Validate connection count
        if connection_count > self.interactive_rules["max_connections"]:
            warnings.append(
                ValidationIssue(
                    type="warning",
                    message=f"Diagram has many connections ({connection_count})",
                    suggestion="Simplify connections for better readability",
                )
            )

        return {
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
        }

    def _get_performance_suggestions(self, diagram_code: str) -> List[ValidationIssue]:
        """Get performance-related suggestions."""
        suggestions = []

        lines = diagram_code.strip().split("\n")

        # Check for complex styling
        style_count = sum(1 for line in lines if "classDef" in line or "class" in line)
        if style_count > 10:
            suggestions.append(
                ValidationIssue(
                    type="info",
                    message="Many style definitions detected",
                    suggestion="Consider using fewer, reusable styles for better performance",
                )
            )

        # Check for long labels
        long_label_count = 0
        for line in lines:
            if "[" in line and "]" in line:
                # Extract label (simplified)
                start = line.find("[")
                end = line.find("]", start)
                if end > start:
                    label = line[start + 1 : end]
                    if len(label) > 30:
                        long_label_count += 1

        if long_label_count > 5:
            suggestions.append(
                ValidationIssue(
                    type="info",
                    message="Several elements have long labels",
                    suggestion="Use shorter labels for better rendering performance",
                )
            )

        return suggestions

    def _get_accessibility_suggestions(
        self, diagram_code: str
    ) -> List[ValidationIssue]:
        """Get accessibility-related suggestions."""
        suggestions = []

        lines = diagram_code.strip().split("\n")

        # Check for title
        has_title = any("title" in line.lower() for line in lines)
        if not has_title:
            suggestions.append(
                ValidationIssue(
                    type="info",
                    message="Diagram has no title",
                    suggestion="Add a title for better accessibility",
                )
            )

        # Check for descriptive labels
        short_label_count = 0
        for line in lines:
            if "[" in line and "]" in line:
                # Extract label (simplified)
                start = line.find("[")
                end = line.find("]", start)
                if end > start:
                    label = line[start + 1 : end]
                    if len(label.strip()) < 3:
                        short_label_count += 1

        if short_label_count > 3:
            suggestions.append(
                ValidationIssue(
                    type="info",
                    message="Several elements have very short labels",
                    suggestion="Use more descriptive labels for better accessibility",
                )
            )

        return suggestions

    def _get_error_suggestion(self, error: str) -> Optional[str]:
        """Get suggestion for error message."""
        error_suggestions = {
            "Unknown or invalid diagram type": "Check the first line of your diagram",
            "Empty diagram": "Add some elements to your diagram",
            "Unmatched bracket": "Check for balanced brackets in node definitions",
            "Invalid syntax": "Review the Mermaid syntax documentation",
        }

        for pattern, suggestion in error_suggestions.items():
            if pattern.lower() in error.lower():
                return suggestion

        return None

    def _get_warning_suggestion(self, warning: str) -> Optional[str]:
        """Get suggestion for warning message."""
        warning_suggestions = {
            "Non-standard node ID": "Use alphanumeric characters for node IDs",
            "Long label": "Consider using shorter, more concise labels",
            "Complex structure": "Break down into smaller, simpler diagrams",
        }

        for pattern, suggestion in warning_suggestions.items():
            if pattern.lower() in warning.lower():
                return suggestion

        return None
