"""
Unit tests for mcp.prompts.extended module.

Tests for extended prompts (ER, state, gantt, mindmap, etc.).
"""

import pytest

from mermaid_render.mcp.prompts.extended import (
    convert_to_diagram_prompt,
    document_architecture_prompt,
    generate_c4_diagram_prompt,
    generate_er_diagram_prompt,
    generate_gantt_chart_prompt,
    generate_git_graph_prompt,
    generate_mindmap_prompt,
    generate_pie_chart_prompt,
    generate_state_diagram_prompt,
    generate_timeline_prompt,
    refactor_diagram_prompt,
    translate_diagram_prompt,
)


@pytest.mark.unit
class TestGenerateERDiagramPrompt:
    """Tests for generate_er_diagram_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_er_diagram_prompt("A customer order database")
        assert isinstance(result, str)

    def test_includes_description(self):
        """Test prompt includes description."""
        description = "A customer order database"
        result = generate_er_diagram_prompt(description)
        assert description in result

    def test_with_attributes(self):
        """Test with attributes included."""
        result = generate_er_diagram_prompt(
            "A database", include_attributes=True
        )
        assert "attribute" in result.lower()

    def test_with_relationships(self):
        """Test with relationships included."""
        result = generate_er_diagram_prompt(
            "A database", include_relationships=True
        )
        assert "relationship" in result.lower() or "cardinality" in result.lower()

    def test_crow_foot_notation(self):
        """Test crow foot notation style."""
        result = generate_er_diagram_prompt(
            "A database", notation_style="crow_foot"
        )
        assert isinstance(result, str)


@pytest.mark.unit
class TestGenerateStateDiagramPrompt:
    """Tests for generate_state_diagram_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_state_diagram_prompt("A traffic light system")
        assert isinstance(result, str)

    def test_includes_description(self):
        """Test prompt includes description."""
        description = "A traffic light system"
        result = generate_state_diagram_prompt(description)
        assert description in result

    def test_with_transitions(self):
        """Test with transitions included."""
        result = generate_state_diagram_prompt(
            "A system", include_transitions=True
        )
        assert "transition" in result.lower()

    def test_with_actions(self):
        """Test with actions included."""
        result = generate_state_diagram_prompt(
            "A system", include_actions=True
        )
        assert "action" in result.lower() or "entry" in result.lower()


@pytest.mark.unit
class TestGenerateGanttChartPrompt:
    """Tests for generate_gantt_chart_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_gantt_chart_prompt("A software development project")
        assert isinstance(result, str)

    def test_includes_description(self):
        """Test prompt includes description."""
        description = "A software development project"
        result = generate_gantt_chart_prompt(description)
        assert description in result

    def test_with_dependencies(self):
        """Test with dependencies included."""
        result = generate_gantt_chart_prompt(
            "A project", include_dependencies=True
        )
        assert "depend" in result.lower() or "after" in result.lower()

    def test_with_milestones(self):
        """Test with milestones included."""
        result = generate_gantt_chart_prompt(
            "A project", include_milestones=True
        )
        assert "milestone" in result.lower()


@pytest.mark.unit
class TestGenerateMindmapPrompt:
    """Tests for generate_mindmap_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_mindmap_prompt("Machine learning concepts")
        assert isinstance(result, str)

    def test_includes_description(self):
        """Test prompt includes description."""
        description = "Machine learning concepts"
        result = generate_mindmap_prompt(description)
        assert description in result

    def test_depth_level(self):
        """Test depth level parameter."""
        result = generate_mindmap_prompt("A topic", depth_level=3)
        assert isinstance(result, str)

    def test_with_icons(self):
        """Test with icons included."""
        result = generate_mindmap_prompt("A topic", include_icons=True)
        assert "icon" in result.lower()


@pytest.mark.unit
class TestGenerateTimelinePrompt:
    """Tests for generate_timeline_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_timeline_prompt("History of computing")
        assert isinstance(result, str)

    def test_includes_description(self):
        """Test prompt includes description."""
        description = "History of computing"
        result = generate_timeline_prompt(description)
        assert description in result

    def test_time_scale(self):
        """Test time scale parameter."""
        result = generate_timeline_prompt("Events", time_scale="years")
        assert isinstance(result, str)


@pytest.mark.unit
class TestGeneratePieChartPrompt:
    """Tests for generate_pie_chart_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_pie_chart_prompt("Market share distribution")
        assert isinstance(result, str)

    def test_includes_description(self):
        """Test prompt includes description."""
        description = "Market share distribution"
        result = generate_pie_chart_prompt(description)
        assert description in result

    def test_with_percentages(self):
        """Test with percentages shown."""
        result = generate_pie_chart_prompt("Data", show_percentages=True)
        assert "percent" in result.lower()


@pytest.mark.unit
class TestGenerateGitGraphPrompt:
    """Tests for generate_git_graph_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_git_graph_prompt("Feature branch workflow")
        assert isinstance(result, str)

    def test_includes_description(self):
        """Test prompt includes description."""
        description = "Feature branch workflow"
        result = generate_git_graph_prompt(description)
        assert description in result

    def test_with_branches(self):
        """Test with branches included."""
        result = generate_git_graph_prompt("Workflow", include_branches=True)
        assert "branch" in result.lower()

    def test_with_tags(self):
        """Test with tags included."""
        result = generate_git_graph_prompt("Workflow", include_tags=True)
        assert "tag" in result.lower()

    def test_gitflow_strategy(self):
        """Test gitflow branching strategy."""
        result = generate_git_graph_prompt(
            "Workflow", branching_strategy="gitflow"
        )
        assert "gitflow" in result.lower() or "develop" in result.lower()


@pytest.mark.unit
class TestGenerateC4DiagramPrompt:
    """Tests for generate_c4_diagram_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = generate_c4_diagram_prompt("E-commerce system")
        assert isinstance(result, str)

    def test_includes_description(self):
        """Test prompt includes description."""
        description = "E-commerce system"
        result = generate_c4_diagram_prompt(description)
        assert description in result

    def test_context_level(self):
        """Test context diagram level."""
        result = generate_c4_diagram_prompt("System", diagram_level="context")
        assert "context" in result.lower()

    def test_container_level(self):
        """Test container diagram level."""
        result = generate_c4_diagram_prompt("System", diagram_level="container")
        assert "container" in result.lower()

    def test_with_external(self):
        """Test with external systems included."""
        result = generate_c4_diagram_prompt("System", include_external=True)
        assert "external" in result.lower()


@pytest.mark.unit
class TestRefactorDiagramPrompt:
    """Tests for refactor_diagram_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = refactor_diagram_prompt("flowchart TD\n    A --> B")
        assert isinstance(result, str)

    def test_includes_diagram_code(self):
        """Test prompt includes diagram code."""
        code = "flowchart TD\n    A --> B"
        result = refactor_diagram_prompt(code)
        assert "A --> B" in result

    def test_with_refactoring_goals(self):
        """Test with refactoring goals."""
        goals = ["Improve readability", "Add styling"]
        result = refactor_diagram_prompt(
            "flowchart TD\n    A --> B", refactoring_goals=goals
        )
        for goal in goals:
            assert goal in result

    def test_preserve_semantics(self):
        """Test preserve semantics option."""
        result = refactor_diagram_prompt(
            "flowchart TD\n    A --> B", preserve_semantics=True
        )
        assert "preserve" in result.lower() or "meaning" in result.lower()


@pytest.mark.unit
class TestTranslateDiagramPrompt:
    """Tests for translate_diagram_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = translate_diagram_prompt(
            "flowchart TD\n    A[Start] --> B[End]", "Chinese"
        )
        assert isinstance(result, str)

    def test_includes_diagram_code(self):
        """Test prompt includes diagram code."""
        code = "flowchart TD\n    A[Start] --> B[End]"
        result = translate_diagram_prompt(code, "Spanish")
        assert "Start" in result

    def test_includes_target_language(self):
        """Test prompt includes target language."""
        result = translate_diagram_prompt(
            "flowchart TD\n    A --> B", "French"
        )
        assert "French" in result

    def test_preserve_technical_terms(self):
        """Test preserve technical terms option."""
        result = translate_diagram_prompt(
            "flowchart TD\n    A --> B", "German", preserve_technical_terms=True
        )
        assert "technical" in result.lower()


@pytest.mark.unit
class TestConvertToDiagramPrompt:
    """Tests for convert_to_diagram_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = convert_to_diagram_prompt("json", '{"key": "value"}')
        assert isinstance(result, str)

    def test_includes_source_content(self):
        """Test prompt includes source content."""
        content = '{"key": "value"}'
        result = convert_to_diagram_prompt("json", content)
        assert "key" in result

    def test_includes_source_format(self):
        """Test prompt includes source format."""
        result = convert_to_diagram_prompt("json", '{}')
        assert "json" in result.lower()

    def test_target_diagram_type(self):
        """Test target diagram type."""
        result = convert_to_diagram_prompt(
            "json", '{}', target_diagram_type="flowchart"
        )
        assert "flowchart" in result.lower()


@pytest.mark.unit
class TestDocumentArchitecturePrompt:
    """Tests for document_architecture_prompt function."""

    def test_returns_string(self):
        """Test function returns a string."""
        result = document_architecture_prompt(
            "My System", ["Frontend", "Backend", "Database"]
        )
        assert isinstance(result, str)

    def test_includes_system_name(self):
        """Test prompt includes system name."""
        name = "My System"
        result = document_architecture_prompt(name, ["Component"])
        assert name in result

    def test_includes_components(self):
        """Test prompt includes components."""
        components = ["Frontend", "Backend", "Database"]
        result = document_architecture_prompt("System", components)
        for component in components:
            assert component in result

    def test_with_interactions(self):
        """Test with interactions."""
        interactions = ["Frontend calls Backend", "Backend queries Database"]
        result = document_architecture_prompt(
            "System", ["A", "B"], interactions=interactions
        )
        for interaction in interactions:
            assert interaction in result

    def test_with_diagram_types(self):
        """Test with diagram types."""
        diagram_types = ["flowchart", "sequence"]
        result = document_architecture_prompt(
            "System", ["A", "B"], diagram_types=diagram_types
        )
        for dt in diagram_types:
            assert dt in result.lower()
