"""
Validation module for the Mermaid Render library.

This module provides validation functionality for Mermaid diagram syntax,
ensuring diagrams are well-formed before rendering.
"""

from .validator import MermaidValidator, ValidationResult

__all__ = ["MermaidValidator", "ValidationResult"]
