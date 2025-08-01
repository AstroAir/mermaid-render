"""
Unit tests for validation functionality.
"""


from mermaid_render.validators import MermaidValidator, ValidationResult


class TestValidationResult:
    """Test ValidationResult class."""

    def test_valid_result(self):
        """Test valid validation result."""
        result = ValidationResult(
            is_valid=True, errors=[], warnings=["Minor warning"], line_errors={}
        )

        assert result.is_valid
        assert bool(result) is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert "Valid" in str(result)

    def test_invalid_result(self):
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

    def test_init(self):
        """Test validator initialization."""
        validator = MermaidValidator()

        assert len(validator.errors) == 0
        assert len(validator.warnings) == 0
        assert len(validator.line_errors) == 0

    def test_validate_empty_code(self):
        """Test validation of empty code."""
        validator = MermaidValidator()

        result = validator.validate("")

        assert not result.is_valid
        assert "Empty diagram code" in result.errors

    def test_validate_whitespace_only(self):
        """Test validation of whitespace-only code."""
        validator = MermaidValidator()

        result = validator.validate("   \n  \t  \n  ")

        assert not result.is_valid
        assert "Empty diagram code" in result.errors

    def test_validate_valid_flowchart(self):
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

    def test_validate_valid_sequence(self):
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

    def test_validate_invalid_diagram_type(self):
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

    def test_validate_unmatched_brackets(self):
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

    def test_detect_diagram_type_flowchart(self):
        """Test diagram type detection for flowchart."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("flowchart TD") == "flowchart"
        assert validator._detect_diagram_type("flowchart LR") == "flowchart"
        assert validator._detect_diagram_type("flowchart TB") == "flowchart"

    def test_detect_diagram_type_sequence(self):
        """Test diagram type detection for sequence."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("sequenceDiagram") == "sequenceDiagram"

    def test_detect_diagram_type_class(self):
        """Test diagram type detection for class diagram."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("classDiagram") == "classDiagram"

    def test_detect_diagram_type_state(self):
        """Test diagram type detection for state diagram."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("stateDiagram") == "stateDiagram"
        assert validator._detect_diagram_type("stateDiagram-v2") == "stateDiagram"

    def test_detect_diagram_type_unknown(self):
        """Test diagram type detection for unknown type."""
        validator = MermaidValidator()

        assert validator._detect_diagram_type("unknownDiagram") is None
        assert validator._detect_diagram_type("") is None

    def test_validate_node_id_valid(self):
        """Test validation of valid node IDs."""
        validator = MermaidValidator()

        assert validator.validate_node_id("A")
        assert validator.validate_node_id("Node1")
        assert validator.validate_node_id("my_node")
        assert validator.validate_node_id("nodeABC123")

    def test_validate_node_id_invalid(self):
        """Test validation of invalid node IDs."""
        validator = MermaidValidator()

        assert not validator.validate_node_id("1Node")  # Starts with number
        assert not validator.validate_node_id("node-with-dash")  # Contains dash
        assert not validator.validate_node_id("node with space")  # Contains space
        assert not validator.validate_node_id("")  # Empty

    def test_suggest_fixes_unknown_type(self):
        """Test fix suggestions for unknown diagram type."""
        validator = MermaidValidator()

        suggestions = validator.suggest_fixes("unknownDiagram\nA --> B")

        assert any(
            "diagram type declaration" in suggestion for suggestion in suggestions
        )

    def test_suggest_fixes_unmatched_brackets(self):
        """Test fix suggestions for unmatched brackets."""
        validator = MermaidValidator()

        code = """
flowchart TD
    A[Start --> B
"""

        suggestions = validator.suggest_fixes(code)

        assert any("bracket" in suggestion for suggestion in suggestions)

    def test_suggest_fixes_empty_diagram(self):
        """Test fix suggestions for empty diagram."""
        validator = MermaidValidator()

        suggestions = validator.suggest_fixes("")

        assert any("diagram content" in suggestion for suggestion in suggestions)

    def test_validate_flowchart_specific(self):
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

    def test_validate_sequence_specific(self):
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

    def test_validate_class_specific(self):
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

    def test_validation_warnings(self):
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
