"""
Enhanced validation system for the Mermaid Render library.

This module provides comprehensive input validation and sanitization
for the plugin-based rendering system.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_input: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class InputValidator:
    """
    Enhanced input validator for Mermaid diagrams.

    This class provides comprehensive validation and sanitization
    of Mermaid diagram inputs, including syntax checking, security
    validation, and format-specific requirements.
    """

    def __init__(self) -> None:
        """Initialize the input validator."""
        self.logger = logging.getLogger(__name__)

        # Security patterns to detect potentially dangerous content
        self._security_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',  # Event handlers
            r'<iframe[^>]*>',  # Iframes
            r'<object[^>]*>',  # Objects
            r'<embed[^>]*>',  # Embeds
        ]

        # Known diagram types and their patterns
        self._diagram_types = {
            'flowchart': [r'flowchart\s+(TD|TB|BT|RL|LR)', r'graph\s+(TD|TB|BT|RL|LR)'],
            'sequence': [r'sequenceDiagram'],
            'class': [r'classDiagram'],
            'state': [r'stateDiagram(-v2)?'],
            'er': [r'erDiagram'],
            'gantt': [r'gantt'],
            'pie': [r'pie(\s+title)?'],
            'journey': [r'journey'],
            'gitgraph': [r'gitGraph'],
            'mindmap': [r'mindmap'],
            'timeline': [r'timeline'],
            'quadrant': [r'quadrantChart'],
        }

        # Maximum limits for safety
        self._limits = {
            'max_length': 100000,  # 100KB
            'max_lines': 1000,
            'max_nodes': 500,
            'max_edges': 1000,
        }

    def validate(
        self,
        mermaid_code: str,
        format: str,
        renderer_name: Optional[str] = None,
        strict: bool = False,
    ) -> ValidationResult:
        """
        Validate Mermaid diagram input.

        Args:
            mermaid_code: Raw Mermaid diagram syntax
            format: Target output format
            renderer_name: Target renderer name
            strict: Whether to use strict validation

        Returns:
            ValidationResult with validation details
        """
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {}

        # Basic input validation
        if not mermaid_code or not mermaid_code.strip():
            errors.append("Empty or whitespace-only input")
            return ValidationResult(False, errors, warnings, metadata=metadata)

        # Length validation
        if len(mermaid_code) > self._limits['max_length']:
            errors.append(
                f"Input too long: {len(mermaid_code)} > {self._limits['max_length']} characters")

        # Line count validation
        lines = mermaid_code.split('\n')
        if len(lines) > self._limits['max_lines']:
            errors.append(f"Too many lines: {len(lines)} > {self._limits['max_lines']}")

        # Security validation
        security_issues = self._check_security(mermaid_code)
        if security_issues:
            errors.extend(security_issues)

        # Diagram type validation
        diagram_type = self._detect_diagram_type(mermaid_code)
        metadata['diagram_type'] = diagram_type

        if not diagram_type:
            if strict:
                errors.append("Could not detect diagram type")
            else:
                warnings.append("Could not detect diagram type - assuming flowchart")
                diagram_type = 'flowchart'

        # Renderer compatibility validation
        if renderer_name:
            compatibility_issues = self._check_renderer_compatibility(
                diagram_type, format, renderer_name
            )
            if compatibility_issues:
                if strict:
                    errors.extend(compatibility_issues)
                else:
                    warnings.extend(compatibility_issues)

        # Syntax validation (basic)
        syntax_issues = self._check_basic_syntax(mermaid_code, diagram_type)
        if syntax_issues:
            if strict:
                errors.extend(syntax_issues)
            else:
                warnings.extend(syntax_issues)

        # Complexity validation
        complexity_issues = self._check_complexity(mermaid_code)
        warnings.extend(complexity_issues)

        # Sanitize input if no critical errors
        sanitized_input = None
        if not errors:
            sanitized_input = self._sanitize_input(mermaid_code)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_input=sanitized_input,
            metadata=metadata,
        )

    def _check_security(self, mermaid_code: str) -> List[str]:
        """Check for security issues in the input."""
        issues = []

        for pattern in self._security_patterns:
            if re.search(pattern, mermaid_code, re.IGNORECASE | re.DOTALL):
                issues.append(f"Potentially dangerous content detected: {pattern}")

        return issues

    def _detect_diagram_type(self, mermaid_code: str) -> Optional[str]:
        """Detect the diagram type from the input."""
        for diagram_type, patterns in self._diagram_types.items():
            for pattern in patterns:
                if re.search(pattern, mermaid_code, re.IGNORECASE):
                    return diagram_type
        return None

    def _check_renderer_compatibility(
        self,
        diagram_type: Optional[str],
        format: str,
        renderer_name: str,
    ) -> List[str]:
        """Check renderer compatibility with diagram type and format."""
        issues = []

        # Graphviz renderer limitations
        if renderer_name == "graphviz":
            if diagram_type not in ["flowchart", None]:
                issues.append(
                    f"Graphviz renderer only supports flowcharts, got {diagram_type}"
                )

        # Format-specific checks
        if format == "pdf" and renderer_name == "graphviz":
            # Graphviz PDF support might be limited
            pass

        return issues

    def _check_basic_syntax(self, mermaid_code: str, diagram_type: Optional[str]) -> List[str]:
        """Perform basic syntax validation."""
        issues = []

        # Check for balanced brackets
        bracket_count = mermaid_code.count('[') - mermaid_code.count(']')
        if bracket_count != 0:
            issues.append(
                f"Unbalanced brackets: {bracket_count} extra opening brackets")

        # Check for balanced parentheses
        paren_count = mermaid_code.count('(') - mermaid_code.count(')')
        if paren_count != 0:
            issues.append(
                f"Unbalanced parentheses: {paren_count} extra opening parentheses")

        # Check for empty lines that might cause issues
        lines = mermaid_code.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('%%'):  # Ignore comments
                # Check for common syntax errors
                if stripped.endswith('-->') or stripped.endswith('---'):
                    issues.append(f"Line {i}: Incomplete edge definition")

        return issues

    def _check_complexity(self, mermaid_code: str) -> List[str]:
        """Check diagram complexity and warn about potential issues."""
        warnings = []

        # Count nodes (rough estimate)
        node_count = len(re.findall(r'\w+\[.*?\]', mermaid_code))
        if node_count > self._limits['max_nodes']:
            warnings.append(f"High node count ({node_count}) may impact performance")

        # Count edges (rough estimate)
        edge_count = len(re.findall(r'-->', mermaid_code)) + \
            len(re.findall(r'---', mermaid_code))
        if edge_count > self._limits['max_edges']:
            warnings.append(f"High edge count ({edge_count}) may impact performance")

        # Check for very long labels
        long_labels = re.findall(r'\[(.{50,})\]', mermaid_code)
        if long_labels:
            warnings.append(
                f"Found {len(long_labels)} very long labels that may affect layout")

        return warnings

    def _sanitize_input(self, mermaid_code: str) -> str:
        """Sanitize input by removing potentially dangerous content."""
        sanitized = mermaid_code

        # Remove script tags and JavaScript
        for pattern in self._security_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)

        # Normalize line endings
        sanitized = sanitized.replace('\r\n', '\n').replace('\r', '\n')

        # Remove excessive whitespace
        lines = sanitized.split('\n')
        cleaned_lines = []
        for line in lines:
            # Keep indentation but remove trailing whitespace
            cleaned_line = line.rstrip()
            cleaned_lines.append(cleaned_line)

        # Remove excessive empty lines (more than 2 consecutive)
        final_lines = []
        empty_count = 0
        for line in cleaned_lines:
            if line.strip():
                final_lines.append(line)
                empty_count = 0
            else:
                empty_count += 1
                if empty_count <= 2:
                    final_lines.append(line)

        return '\n'.join(final_lines)


# Global validator instance
_global_validator: Optional[InputValidator] = None


def get_global_validator() -> InputValidator:
    """Get the global input validator instance."""
    global _global_validator
    if _global_validator is None:
        _global_validator = InputValidator()
    return _global_validator
