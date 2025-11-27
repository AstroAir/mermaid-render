"""
Unit tests for mcp.prompts.generation module.

Tests for diagram generation prompts.
"""

import pytest

from mermaid_render.mcp.prompts.generation import (
    generate_class_diagram_prompt,
    generate_flowchart_prompt,
    generate_sequence_prompt,
)


@pytest.mark.unit
class TestGenerateFlowchartPrompt:
    """Tests for generate_flowchart_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_flowchart_prompt("A simple login process")
        assert isinstance(result, str)

    def test_includes_process_description(self):
        """Test prompt includes process description."""
        description = "A simple login process"
        result = generate_flowchart_prompt(description)
        assert description in result

    def test_simple_complexity(self):
        """Test simple complexity level."""
        result = generate_flowchart_prompt(
            "A simple process", complexity_level="simple"
        )
        assert isinstance(result, str)
        assert "simple" in result.lower() or "3-7" in result

    def test_medium_complexity(self):
        """Test medium complexity level."""
        result = generate_flowchart_prompt(
            "A process", complexity_level="medium"
        )
        assert isinstance(result, str)

    def test_complex_complexity(self):
        """Test complex complexity level."""
        result = generate_flowchart_prompt(
            "A process", complexity_level="complex"
        )
        assert isinstance(result, str)

    def test_with_decision_points(self):
        """Test with decision points included."""
        result = generate_flowchart_prompt(
            "A process", include_decision_points=True
        )
        assert "decision" in result.lower()

    def test_without_decision_points(self):
        """Test without decision points."""
        result = generate_flowchart_prompt(
            "A process", include_decision_points=False
        )
        assert isinstance(result, str)

    def test_includes_mermaid_instructions(self):
        """Test prompt includes Mermaid instructions."""
        result = generate_flowchart_prompt("A process")
        assert "flowchart" in result.lower() or "mermaid" in result.lower()


@pytest.mark.unit
class TestGenerateSequencePrompt:
    """Tests for generate_sequence_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_sequence_prompt(
            "API authentication flow", ["Client", "Server"]
        )
        assert isinstance(result, str)

    def test_includes_interaction_description(self):
        """Test prompt includes interaction description."""
        description = "API authentication flow"
        result = generate_sequence_prompt(description, ["Client", "Server"])
        assert description in result

    def test_includes_participants(self):
        """Test prompt includes participants."""
        participants = ["Client", "Server", "Database"]
        result = generate_sequence_prompt("A flow", participants)
        for participant in participants:
            assert participant in result

    def test_with_notes(self):
        """Test with notes included."""
        result = generate_sequence_prompt(
            "A flow", ["A", "B"], include_notes=True
        )
        assert "note" in result.lower()

    def test_without_notes(self):
        """Test without notes."""
        result = generate_sequence_prompt(
            "A flow", ["A", "B"], include_notes=False
        )
        assert isinstance(result, str)

    def test_includes_sequence_instructions(self):
        """Test prompt includes sequence diagram instructions."""
        result = generate_sequence_prompt("A flow", ["A", "B"])
        assert "sequencediagram" in result.lower() or "sequence" in result.lower()


@pytest.mark.unit
class TestGenerateClassDiagramPrompt:
    """Tests for generate_class_diagram_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_class_diagram_prompt("A user management system")
        assert isinstance(result, str)

    def test_includes_system_description(self):
        """Test prompt includes system description."""
        description = "A user management system"
        result = generate_class_diagram_prompt(description)
        assert description in result

    def test_with_methods(self):
        """Test with methods included."""
        result = generate_class_diagram_prompt(
            "A system", include_methods=True
        )
        assert "method" in result.lower()

    def test_without_methods(self):
        """Test without methods."""
        result = generate_class_diagram_prompt(
            "A system", include_methods=False
        )
        assert isinstance(result, str)

    def test_with_relationships(self):
        """Test with relationships included."""
        result = generate_class_diagram_prompt(
            "A system", include_relationships=True
        )
        assert "relationship" in result.lower() or "inheritance" in result.lower()

    def test_without_relationships(self):
        """Test without relationships."""
        result = generate_class_diagram_prompt(
            "A system", include_relationships=False
        )
        assert isinstance(result, str)

    def test_includes_class_instructions(self):
        """Test prompt includes class diagram instructions."""
        result = generate_class_diagram_prompt("A system")
        assert "classdiagram" in result.lower() or "class" in result.lower()
