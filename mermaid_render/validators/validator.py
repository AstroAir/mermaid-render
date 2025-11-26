"""
Mermaid syntax validator for the Mermaid Render library.

This module provides comprehensive validation of Mermaid diagram syntax,
checking for common errors, structural issues, and best practices. It supports
all major Mermaid diagram types and provides detailed error reporting with
line-specific feedback.

The validator performs multiple levels of validation:
- Syntax validation: Checks for proper Mermaid syntax
- Structural validation: Ensures diagram structure is correct
- Semantic validation: Validates logical consistency
- Best practice validation: Suggests improvements

Example:
    >>> from mermaid_render.validators import MermaidValidator
    >>>
    >>> validator = MermaidValidator()
    >>> result = validator.validate('''
    ... flowchart TD
    ...     A[Start] --> B[Process]
    ...     B --> C[End]
    ... ''')
    >>>
    >>> if result.is_valid:
    ...     print("✓ Diagram is valid")
    ... else:
    ...     for error in result.errors:
    ...         print(f"✗ {error}")
"""

import re
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """
    Result of Mermaid syntax validation.

    Contains the validation status and detailed information about any errors
    or warnings found during validation. Provides both programmatic access
    to validation details and human-readable formatting.

    Attributes:
        is_valid (bool): True if the diagram passed validation
        errors (List[str]): List of error messages for validation failures
        warnings (List[str]): List of warning messages for potential issues
        line_errors (Dict[int, List[str]]): Mapping of line numbers to specific errors

    Example:
        >>> result = validator.validate(diagram_code)
        >>> if result.is_valid:
        ...     print("Validation passed!")
        ... else:
        ...     print(f"Found {len(result.errors)} errors:")
        ...     for error in result.errors:
        ...         print(f"  - {error}")
        ...
        ...     # Check line-specific errors
        ...     for line_num, line_errors in result.line_errors.items():
        ...         print(f"Line {line_num}: {', '.join(line_errors)}")
    """

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    line_errors: dict[int, list[str]]

    def __bool__(self) -> bool:
        """
        Return True if validation passed.

        Allows using ValidationResult in boolean contexts.

        Returns:
            bool: True if is_valid is True

        Example:
            >>> result = validator.validate(code)
            >>> if result:  # Same as: if result.is_valid:
            ...     print("Valid diagram")
        """
        return self.is_valid

    def __str__(self) -> str:
        """
        Return human-readable validation result.

        Provides a concise summary of the validation status including
        error and warning counts.

        Returns:
            str: Formatted validation status

        Example:
            >>> result = validator.validate(code)
            >>> print(result)
            ✓ Valid (with 2 warnings)
            # or
            ✗ Invalid (3 errors, 1 warning)
        """
        if self.is_valid:
            status = "✓ Valid"
            if self.warnings:
                status += f" (with {len(self.warnings)} warnings)"
        else:
            status = f"✗ Invalid ({len(self.errors)} errors"
            if self.warnings:
                status += f", {len(self.warnings)} warnings"
            status += ")"

        return status


class MermaidValidator:
    """
    Comprehensive Mermaid syntax validator.

    Validates Mermaid diagram syntax for common errors, structural issues,
    and best practices.
    """

    # Known diagram types and their patterns
    DIAGRAM_TYPES = {
        "flowchart": r"^flowchart\s+(TD|TB|BT|RL|LR)",
        "sequenceDiagram": r"^sequenceDiagram",
        "classDiagram": r"^classDiagram",
        "stateDiagram": r"^stateDiagram(-v2)?",
        "erDiagram": r"^erDiagram",
        "journey": r"^journey",
        "gantt": r"^gantt",
        "pie": r"^pie",
        "gitgraph": r"^gitgraph",
        "mindmap": r"^mindmap",
        "timeline": r"^timeline",
    }

    # Common syntax patterns
    PATTERNS = {
        "node_id": r"^[A-Za-z][A-Za-z0-9_]*$",
        "flowchart_arrow": r"-->|---|-\.-|-.->|==>|===",
        "sequence_arrow": r"->|->>|-->>|-\)|--\)",
    }

    def __init__(self) -> None:
        """Initialize the validator."""
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.line_errors: dict[int, list[str]] = {}
        self.current_diagram_type: str | None = None

    def validate(self, mermaid_code: str) -> ValidationResult:
        """
        Validate Mermaid diagram syntax.

        Args:
            mermaid_code: Raw Mermaid diagram code

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        self._reset()

        if not mermaid_code or not mermaid_code.strip():
            self.errors.append("Empty diagram code")
            return self._create_result()

        lines = mermaid_code.strip().split("\n")

        # Basic structure validation
        self._validate_structure(lines)

        # Diagram type specific validation
        diagram_type = self._detect_diagram_type(lines[0])
        self.current_diagram_type = diagram_type
        if diagram_type:
            self._validate_diagram_type(lines, diagram_type)
        else:
            self.errors.append(f"Unknown or invalid diagram type: {lines[0]}")

        # General syntax validation
        self._validate_syntax(lines)

        return self._create_result()

    def _reset(self) -> None:
        """Reset validation state."""
        self.errors.clear()
        self.warnings.clear()
        self.line_errors.clear()
        self.current_diagram_type = None

    def _create_result(self) -> ValidationResult:
        """Create validation result."""
        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors.copy(),
            warnings=self.warnings.copy(),
            line_errors=self.line_errors.copy(),
        )

    def _add_error(self, message: str, line_number: int | None = None) -> None:
        """Add an error message."""
        self.errors.append(message)
        if line_number is not None:
            if line_number not in self.line_errors:
                self.line_errors[line_number] = []
            self.line_errors[line_number].append(message)

    def _add_warning(self, message: str, line_number: int | None = None) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def _detect_diagram_type(self, first_line: str) -> str | None:
        """Detect the diagram type from the first line."""
        first_line = first_line.strip()

        for diagram_type, pattern in self.DIAGRAM_TYPES.items():
            if re.match(pattern, first_line):
                return diagram_type

        return None

    def _validate_structure(self, lines: list[str]) -> None:
        """Validate basic diagram structure."""
        if not lines:
            self._add_error("Empty diagram")
            return

        # Check for empty lines at start/end
        if not lines[0].strip():
            self._add_warning("Diagram starts with empty line", 1)

        if not lines[-1].strip():
            self._add_warning("Diagram ends with empty line", len(lines))

        # Check for consistent indentation
        self._validate_indentation(lines)

    def _validate_indentation(self, lines: list[str]) -> None:
        """Validate indentation consistency."""
        indent_levels = []

        for _i, line in enumerate(lines, 1):
            if line.strip():  # Skip empty lines
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    indent_levels.append(leading_spaces)

        if indent_levels:
            # Check if indentation is consistent (multiples of common factor)
            if len(set(indent_levels)) > 3:  # Allow some variation
                self._add_warning("Inconsistent indentation detected")

    def _validate_syntax(self, lines: list[str]) -> None:
        """Validate general syntax rules."""
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for common syntax errors
            self._validate_line_syntax(line, i)

    def _validate_line_syntax(self, line: str, line_number: int) -> None:
        """Validate syntax of a single line."""
        # Skip bracket validation for class and ER diagrams as they have special syntax
        if self.current_diagram_type in ["classDiagram", "erDiagram"]:
            return

        # Check for unmatched brackets/parentheses
        brackets = {"(": ")", "[": "]", "{": "}"}
        stack = []

        for char in line:
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if not stack or stack.pop() != char:
                    self._add_error(f"Unmatched bracket: {char}", line_number)
                    return

        if stack:
            self._add_error(f"Unclosed brackets: {stack}", line_number)

    def _validate_diagram_type(self, lines: list[str], diagram_type: str) -> None:
        """Validate diagram-specific syntax."""
        if diagram_type == "flowchart":
            self._validate_flowchart(lines)
        elif diagram_type == "sequenceDiagram":
            self._validate_sequence_diagram(lines)
        elif diagram_type == "classDiagram":
            self._validate_class_diagram(lines)
        elif diagram_type == "timeline":
            self._validate_timeline(lines)
        # Add more diagram-specific validations as needed

    def _validate_flowchart(self, lines: list[str]) -> None:
        """Validate flowchart-specific syntax."""
        nodes = set()

        for i, line in enumerate(lines[1:], 2):  # Skip first line (diagram type)
            line = line.strip()
            if not line:
                continue

            # Check for node definitions and connections
            if "-->" in line or "---" in line:
                # This is a connection line
                parts = re.split(r"-->|---|-\.-|-.->|==>|===", line)
                if len(parts) >= 2:
                    from_node = parts[0].strip()
                    to_node = parts[1].split(":")[0].strip()  # Remove labels

                    # Validate node IDs
                    if from_node and not re.match(self.PATTERNS["node_id"], from_node):
                        self._add_warning(f"Non-standard node ID: {from_node}", i)

                    if to_node and not re.match(self.PATTERNS["node_id"], to_node):
                        self._add_warning(f"Non-standard node ID: {to_node}", i)

                    nodes.update([from_node, to_node])

            # Check for node shape definitions
            elif any(bracket in line for bracket in ["[", "(", "{", ">"]):
                # Extract node ID
                node_match = re.match(r"^(\w+)", line)
                if node_match:
                    nodes.add(node_match.group(1))

        if not nodes:
            self._add_warning("No nodes found in flowchart")

    def _validate_sequence_diagram(self, lines: list[str]) -> None:
        """Validate sequence diagram-specific syntax."""
        participants = set()

        for _i, line in enumerate(lines[1:], 2):
            line = line.strip()
            if not line:
                continue

            # Check for participant declarations
            if line.startswith("participant "):
                parts = line.split(" as ")
                if len(parts) == 2:
                    participant_id = parts[0].replace("participant ", "").strip()
                    participants.add(participant_id)
                else:
                    participant_id = line.replace("participant ", "").strip()
                    participants.add(participant_id)

            # Check for message lines
            elif any(arrow in line for arrow in ["->", "->>", "-->", "-->>"]):
                # Extract participants from message
                for arrow in ["->", "->>", "-->", "-->>"]:
                    if arrow in line:
                        parts = line.split(arrow)
                        if len(parts) >= 2:
                            from_p = parts[0].strip()
                            to_p = parts[1].split(":")[0].strip()
                            participants.update([from_p, to_p])
                        break

        if not participants:
            self._add_warning("No participants found in sequence diagram")

    def _validate_class_diagram(self, lines: list[str]) -> None:
        """Validate class diagram-specific syntax."""
        classes = set()

        for _i, line in enumerate(lines[1:], 2):
            line = line.strip()
            if not line:
                continue

            # Check for class definitions
            if line.startswith("class "):
                class_name = line.split()[1].split("{")[0].strip()
                classes.add(class_name)

            # Check for relationships
            elif any(
                rel in line for rel in ["<|--", "*--", "o--", "-->", "..>", "..|>"]
            ):
                # Extract class names from relationship
                for rel in ["<|--", "*--", "o--", "-->", "..>", "..|>"]:
                    if rel in line:
                        parts = line.split(rel)
                        if len(parts) >= 2:
                            from_class = parts[0].strip()
                            to_class = parts[1].split(":")[0].strip()
                            classes.update([from_class, to_class])
                        break

        if not classes:
            self._add_warning("No classes found in class diagram")

    def _validate_timeline(self, lines: list[str]) -> None:
        """Validate timeline-specific syntax."""
        has_periods = False
        has_events = False
        sections = set()

        for i, original_line in enumerate(
            lines[1:], 2
        ):  # Skip first line (diagram type)
            line = original_line.strip()
            if not line:
                continue

            # Check for title
            if line.startswith("title "):
                continue

            # Check for sections
            if line.startswith("section "):
                section_name = line[8:].strip()
                if section_name:
                    sections.add(section_name)
                else:
                    self._add_error("Empty section name", i)
                continue

            # Check for time periods and events
            if ":" in line:
                has_periods = True
                parts = line.split(":", 1)
                if len(parts) == 2:
                    period = parts[0].strip()
                    event = parts[1].strip()

                    if not period and not original_line.startswith("              :"):
                        self._add_error("Empty time period", i)
                    elif event:
                        has_events = True
                    # Empty event is allowed for time periods without events

        if not has_periods:
            self._add_warning("No time periods found in timeline")
        elif not has_events:
            self._add_warning("No events found in timeline")

    def validate_node_id(self, node_id: str) -> bool:
        """Validate a node ID according to Mermaid rules."""
        return bool(re.match(self.PATTERNS["node_id"], node_id))

    def suggest_fixes(self, mermaid_code: str) -> list[str]:
        """Suggest fixes for common validation errors."""
        suggestions = []
        result = self.validate(mermaid_code)

        if not result.is_valid:
            for error in result.errors:
                if "Unknown or invalid diagram type" in error:
                    suggestions.append(
                        "Check the diagram type declaration (first line)"
                    )
                elif "Unmatched bracket" in error or "Unclosed brackets" in error:
                    suggestions.append("Check for balanced brackets and parentheses")
                elif "Empty diagram" in error:
                    suggestions.append("Add diagram content after the type declaration")

        return suggestions
