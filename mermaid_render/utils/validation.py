"""
Validation utilities for the Mermaid Render library.

This module provides convenient validation functions that wrap the main
MermaidValidator class for common validation tasks. These are lightweight
convenience functions that delegate to the main validator implementation.
"""

from typing import List

from ..validators import MermaidValidator, ValidationResult

# Create a shared validator instance for efficiency
_shared_validator = MermaidValidator()


def validate_mermaid_syntax(mermaid_code: str) -> ValidationResult:
    """
    Validate Mermaid diagram syntax.

    This is a convenience function that creates a validator and validates
    the provided Mermaid code.

    Args:
        mermaid_code: Raw Mermaid diagram syntax

    Returns:
        ValidationResult with validation status and any errors/warnings

    Example:
        >>> result = validate_mermaid_syntax('''
        ... flowchart TD
        ...     A[Start] --> B[Process]
        ...     B --> C[End]
        ... ''')
        >>> if result.is_valid:
        ...     print("Diagram is valid!")
        >>> else:
        ...     print(f"Errors: {result.errors}")
    """
    return _shared_validator.validate(mermaid_code)


def quick_validate(mermaid_code: str) -> bool:
    """
    Quick validation that returns only True/False.

    Args:
        mermaid_code: Raw Mermaid diagram syntax

    Returns:
        True if valid, False otherwise

    Example:
        >>> if quick_validate(my_diagram_code):
        ...     render_diagram(my_diagram_code)
    """
    return _shared_validator.validate(mermaid_code).is_valid


def get_validation_errors(mermaid_code: str) -> List[str]:
    """
    Get list of validation errors for Mermaid code.

    Args:
        mermaid_code: Raw Mermaid diagram syntax

    Returns:
        List of error messages (empty if valid)

    Example:
        >>> errors = get_validation_errors(bad_diagram_code)
        >>> for error in errors:
        ...     print(f"Error: {error}")
    """
    return _shared_validator.validate(mermaid_code).errors


def get_validation_warnings(mermaid_code: str) -> List[str]:
    """
    Get list of validation warnings for Mermaid code.

    Args:
        mermaid_code: Raw Mermaid diagram syntax

    Returns:
        List of warning messages

    Example:
        >>> warnings = get_validation_warnings(diagram_code)
        >>> if warnings:
        ...     print("Warnings found:")
        ...     for warning in warnings:
        ...         print(f"  - {warning}")
    """
    return _shared_validator.validate(mermaid_code).warnings


def suggest_fixes(mermaid_code: str) -> List[str]:
    """
    Get suggestions for fixing validation errors.

    Args:
        mermaid_code: Raw Mermaid diagram syntax

    Returns:
        List of suggested fixes

    Example:
        >>> suggestions = suggest_fixes(broken_diagram)
        >>> for suggestion in suggestions:
        ...     print(f"Suggestion: {suggestion}")
    """
    return _shared_validator.suggest_fixes(mermaid_code)


def validate_node_id(node_id: str) -> bool:
    """
    Validate a node ID according to Mermaid rules.

    Args:
        node_id: Node identifier to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> if validate_node_id("myNode123"):
        ...     flowchart.add_node("myNode123", "My Node")
    """
    return _shared_validator.validate_node_id(node_id)
