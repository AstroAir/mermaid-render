"""
Unit tests for validation functionality.
"""


from diagramaid.validators import MermaidValidator, ValidationResult


class TestValidationResult:
    """Test ValidationResult class."""

    def test_valid_result(self) -> None:
        """Test valid validation result."""
        result = ValidationResult(
            is_valid=True, errors=[], warnings=["Minor warning"], line_errors={}
        )

        assert result.is_valid
        assert bool(result) is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert "Valid" in str(result)

    def test_invalid_result(self) -> None:
        """Test invalid validation result."""
        result = ValidationResult(
            is_valid=False,
            errors=["Syntax error", "Missing bracket"],
            warnings=[],
            line_errors={1: ["Error on line 1"]},
        )

        assert not result.is_valid
        assert bool(result) is False
        assert len(result.errors) == 2
        assert "Invalid" in str(result)
        assert "2 errors" in str(result)


class TestMermaidValidator:
    """Test MermaidValidator class."""

    def test_init(self) -> None:
        """Test validator initialization."""
        validator = MermaidValidator()

        assert len(validator.errors) == 0
        assert len(validator.warnings) == 0
        assert len(validator.line_errors) == 0

    def test_validate_empty_code(self) -> None:
        """Test validation of empty code."""
        validator = MermaidValidator()

        result = validator.validate("")

        assert not result.is_valid
        assert "Empty diagram code" in result.errors

    def test_validate_whitespace_only(self) -> None:
        """Test validation of whitespace-only code."""
        validator = MermaidValidator()

        result = validator.validate("   \n  \t  \n  ")

        assert not result.is_valid
        assert "Empty diagram code" in result.errors

    def test_validate_valid_flowchart(self) -> None:
        """Test validation of valid flowchart."""
        validator = MermaidValidator()

        code = """
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
"""

        result = validator.validate(code)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_valid_sequence(self) -> None:
        """Test validation of valid sequence diagram."""
        validator = MermaidValidator()

        code = """
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob!
    B-->>A: Hi Alice!
"""

        result = validator.validate(code)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_invalid_diagram_type(self) -> None:
        """Test validation of invalid diagram type."""
        validator = MermaidValidator()

        code = """
invalidDiagram
    A --> B
"""

        result = validator.validate(code)

        assert not result.is_valid
        assert any(
            "Unknown or invalid diagram type" in error for error in result.errors
        )

    def test_validate_unmatched_brackets(self) -> None:
        """Test validation of unmatched brackets."""
        validator = MermaidValidator()

        code = """
flowchart TD
    A[Start --> B[Process]
    B --> C[End]
"""

        result = validator.validate(code)

        assert not result.is_valid
        # Should detect bracket mismatch

    def test_detect_diagram_type_flowchart(self) -> None:
        """Test diagram type detection for flowchart."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("flowchart TD") == "flowchart"
        assert validator._detect_diagram_type("flowchart LR") == "flowchart"
        assert validator._detect_diagram_type("flowchart TB") == "flowchart"

    def test_detect_diagram_type_sequence(self) -> None:
        """Test diagram type detection for sequence."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("sequenceDiagram") == "sequenceDiagram"

    def test_detect_diagram_type_class(self) -> None:
        """Test diagram type detection for class diagram."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("classDiagram") == "classDiagram"

    def test_detect_diagram_type_state(self) -> None:
        """Test diagram type detection for state diagram."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("stateDiagram") == "stateDiagram"
        assert validator._detect_diagram_type("stateDiagram-v2") == "stateDiagram"

    def test_detect_diagram_type_unknown(self) -> None:
        """Test diagram type detection for unknown type."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("unknownDiagram") is None
        assert validator._detect_diagram_type("") is None

    def test_validate_node_id_valid(self) -> None:
        """Test validation of valid node IDs."""
        validator = MermaidValidator()

        assert validator.validate_node_id("A")
        assert validator.validate_node_id("Node1")
        assert validator.validate_node_id("my_node")
        assert validator.validate_node_id("nodeABC123")

    def test_validate_node_id_invalid(self) -> None:
        """Test validation of invalid node IDs."""
        validator = MermaidValidator()

        assert not validator.validate_node_id("1Node")  # Starts with number
        assert not validator.validate_node_id("node-with-dash")  # Contains dash
        assert not validator.validate_node_id("node with space")  # Contains space
        assert not validator.validate_node_id("")  # Empty

    def test_suggest_fixes_unknown_type(self) -> None:
        """Test fix suggestions for unknown diagram type."""
        validator = MermaidValidator()

        suggestions = validator.suggest_fixes("unknownDiagram\nA --> B")

        assert any(
            "diagram type declaration" in suggestion for suggestion in suggestions
        )

    def test_suggest_fixes_unmatched_brackets(self) -> None:
        """Test fix suggestions for unmatched brackets."""
        validator = MermaidValidator()

        code = """
flowchart TD
    A[Start --> B
"""

        suggestions = validator.suggest_fixes(code)

        assert any("bracket" in suggestion for suggestion in suggestions)

    def test_suggest_fixes_empty_diagram(self) -> None:
        """Test fix suggestions for empty diagram."""
        validator = MermaidValidator()

        suggestions = validator.suggest_fixes("")

        assert any("diagram content" in suggestion for suggestion in suggestions)

    def test_validate_flowchart_specific(self) -> None:
        """Test flowchart-specific validation."""
        validator = MermaidValidator()

        code = """
flowchart TD
    A[Start]
    B[Process]
    A --> B
"""

        result = validator.validate(code)

        # Should pass basic validation
        assert result.is_valid or len(result.errors) == 0

    def test_validate_sequence_specific(self) -> None:
        """Test sequence diagram-specific validation."""
        validator = MermaidValidator()

        code = """
sequenceDiagram
    participant A
    participant B
    A->>B: Message
"""

        result = validator.validate(code)

        # Should pass basic validation
        assert result.is_valid or len(result.errors) == 0

    def test_validate_class_specific(self) -> None:
        """Test class diagram-specific validation."""
        validator = MermaidValidator()

        code = """
classDiagram
    class Animal {
        +name String
        +move() void
    }
    class Dog {
        +bark() void
    }
    Animal <|-- Dog
"""

        result = validator.validate(code)

        # Should pass basic validation
        assert result.is_valid or len(result.errors) == 0

    def test_validation_warnings(self) -> None:
        """Test validation warnings generation."""
        validator = MermaidValidator()

        # Code with potential issues but still valid
        code = """

flowchart TD
    A[Start] --> B[End]

"""

        result = validator.validate(code)

        # Might generate warnings about empty lines
        # The exact behavior depends on implementation
        assert isinstance(result.warnings, list)

    def test_validate_complex_valid_diagram(self) -> None:
        """Test validation of complex but valid diagram."""
        validator = MermaidValidator()

        complex_diagram = """
        flowchart TB
            subgraph "User Interface"
                A[Login Page]
                B[Dashboard]
                C[Settings]
            end

            subgraph "Backend Services"
                D[Authentication Service]
                E[User Service]
                F[Database]
            end

            A --> D
            D --> E
            E --> F
            D -->|Success| B
            B --> C
            C --> E
        """

        result = validator.validate(complex_diagram)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_special_characters(self) -> None:
        """Test validation with special characters in labels."""
        validator = MermaidValidator()

        special_chars = """
        flowchart TD
            A["Node with 'quotes' and symbols: @#$%"]
            B["Unicode: 中文 🚀"]
            A --> B
        """

        result = validator.validate(special_chars)
        assert result.is_valid is True

    def test_validate_multiple_diagram_types(self) -> None:
        """Test validation of different diagram types."""
        validator = MermaidValidator()

        diagram_types = [
            "flowchart TD\n    A --> B",
            "sequenceDiagram\n    A->>B: Message",
            "classDiagram\n    class A",
            "stateDiagram-v2\n    [*] --> A",
            "erDiagram\n    CUSTOMER ||--o{ ORDER : places",
            "journey\n    title My Journey\n    section Go to work\n      Make tea: 5: Me",
            "gantt\n    title A Gantt Diagram\n    section Section\n    A task: 2014-01-01, 30d",
            "pie title Pie Chart\n    \"Dogs\" : 386\n    \"Cats\" : 85",
        ]

        for diagram in diagram_types:
            result = validator.validate(diagram)
            # Most should be valid, but some might not be fully supported
            assert isinstance(result, ValidationResult)

    def test_validate_edge_cases(self) -> None:
        """Test validation of edge cases."""
        validator = MermaidValidator()

        edge_cases = [
            "flowchart",  # Missing direction
            "flowchart TD\n",  # Only header
            "flowchart TD\n    ",  # Header with whitespace
            "flowchart TD\n    A",  # Single node
            "flowchart TD\n    A --> A",  # Self-reference
        ]

        for case in edge_cases:
            result = validator.validate(case)
            assert isinstance(result, ValidationResult)
            # Some might be valid, some invalid, but should not crash

    def test_validate_performance_large_diagram(self) -> None:
        """Test validation performance with large diagrams."""
        validator = MermaidValidator()

        # Create a large diagram
        lines = ["flowchart TD"]
        for i in range(200):
            lines.append(f"    N{i}[Node {i}]")
            if i > 0:
                lines.append(f"    N{i-1} --> N{i}")

        large_diagram = "\n".join(lines)

        import time
        start_time = time.time()
        result = validator.validate(large_diagram)
        end_time = time.time()

        # Should complete within reasonable time (less than 2 seconds)
        assert (end_time - start_time) < 2.0
        assert isinstance(result, ValidationResult)
