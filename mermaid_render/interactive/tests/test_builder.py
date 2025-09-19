"""Tests for the diagram builder."""

import pytest
from unittest.mock import Mock, patch

from ..builder import DiagramBuilder, DiagramType, ElementType, Position, Size
from ..security import InputSanitizer


class TestDiagramBuilder:
    """Test cases for DiagramBuilder."""

    def test_builder_initialization(self):
        """Test builder initialization."""
        builder = DiagramBuilder(DiagramType.FLOWCHART)
        
        assert builder.diagram_type == DiagramType.FLOWCHART
        assert len(builder.elements) == 0
        assert len(builder.connections) == 0
        assert isinstance(builder.metadata, dict)

    def test_add_element(self):
        """Test adding elements to the builder."""
        builder = DiagramBuilder(DiagramType.FLOWCHART)
        
        element_id = builder.add_element(
            element_type=ElementType.NODE,
            label="Test Node",
            position=Position(100, 100),
            size=Size(120, 60)
        )
        
        assert element_id in builder.elements
        element = builder.elements[element_id]
        assert element.label == "Test Node"
        assert element.position.x == 100
        assert element.position.y == 100

    def test_add_connection(self):
        """Test adding connections between elements."""
        builder = DiagramBuilder(DiagramType.FLOWCHART)
        
        # Add two elements
        element1_id = builder.add_element(
            element_type=ElementType.NODE,
            label="Node 1",
            position=Position(100, 100),
            size=Size(120, 60)
        )
        
        element2_id = builder.add_element(
            element_type=ElementType.NODE,
            label="Node 2",
            position=Position(300, 100),
            size=Size(120, 60)
        )
        
        # Add connection
        connection_id = builder.add_connection(
            source_id=element1_id,
            target_id=element2_id,
            label="Test Connection"
        )
        
        assert connection_id in builder.connections
        connection = builder.connections[connection_id]
        assert connection.source_id == element1_id
        assert connection.target_id == element2_id
        assert connection.label == "Test Connection"

    def test_generate_mermaid_code_flowchart(self):
        """Test generating Mermaid code for flowchart."""
        builder = DiagramBuilder(DiagramType.FLOWCHART)
        
        # Add elements
        start_id = builder.add_element(
            element_type=ElementType.NODE,
            label="Start",
            position=Position(100, 100),
            size=Size(120, 60),
            properties={"shape": "circle"}
        )
        
        end_id = builder.add_element(
            element_type=ElementType.NODE,
            label="End",
            position=Position(300, 100),
            size=Size(120, 60),
            properties={"shape": "circle"}
        )
        
        # Add connection
        builder.add_connection(
            source_id=start_id,
            target_id=end_id
        )
        
        code = builder.generate_mermaid_code()
        
        assert "flowchart TD" in code
        assert "Start" in code
        assert "End" in code
        assert "-->" in code

    def test_load_from_mermaid_code(self):
        """Test loading diagram from Mermaid code."""
        builder = DiagramBuilder(DiagramType.FLOWCHART)
        
        mermaid_code = """
        flowchart TD
            A[Start] --> B[Process]
            B --> C[End]
        """
        
        builder.load_from_mermaid_code(mermaid_code)
        
        # Should have parsed elements
        assert len(builder.elements) > 0
        
        # Check that elements were created
        element_ids = list(builder.elements.keys())
        assert any("A" in element_id or "Start" in builder.elements[element_id].label for element_id in element_ids)

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        builder = DiagramBuilder(DiagramType.FLOWCHART)
        
        # Add some content
        element_id = builder.add_element(
            element_type=ElementType.NODE,
            label="Test",
            position=Position(100, 100),
            size=Size(120, 60)
        )
        
        # Serialize
        data = builder.to_dict()
        
        # Create new builder and deserialize
        new_builder = DiagramBuilder(DiagramType.FLOWCHART)
        new_builder.from_dict(data)
        
        # Check that content was preserved
        assert len(new_builder.elements) == 1
        assert element_id in new_builder.elements
        assert new_builder.elements[element_id].label == "Test"

    def test_update_element(self):
        """Test updating element properties."""
        builder = DiagramBuilder(DiagramType.FLOWCHART)
        
        element_id = builder.add_element(
            element_type=ElementType.NODE,
            label="Original",
            position=Position(100, 100),
            size=Size(120, 60)
        )
        
        # Update element
        success = builder.update_element(
            element_id=element_id,
            label="Updated",
            position=Position(200, 200)
        )
        
        assert success
        element = builder.elements[element_id]
        assert element.label == "Updated"
        assert element.position.x == 200
        assert element.position.y == 200

    def test_remove_element(self):
        """Test removing elements."""
        builder = DiagramBuilder(DiagramType.FLOWCHART)
        
        element_id = builder.add_element(
            element_type=ElementType.NODE,
            label="Test",
            position=Position(100, 100),
            size=Size(120, 60)
        )
        
        # Remove element
        success = builder.remove_element(element_id)
        
        assert success
        assert element_id not in builder.elements

    def test_remove_connection(self):
        """Test removing connections."""
        builder = DiagramBuilder(DiagramType.FLOWCHART)
        
        # Add elements and connection
        element1_id = builder.add_element(
            element_type=ElementType.NODE,
            label="Node 1",
            position=Position(100, 100),
            size=Size(120, 60)
        )
        
        element2_id = builder.add_element(
            element_type=ElementType.NODE,
            label="Node 2",
            position=Position(300, 100),
            size=Size(120, 60)
        )
        
        connection_id = builder.add_connection(
            source_id=element1_id,
            target_id=element2_id
        )
        
        # Remove connection
        success = builder.remove_connection(connection_id)
        
        assert success
        assert connection_id not in builder.connections


class TestInputSanitizer:
    """Test cases for InputSanitizer."""

    def test_sanitize_label_valid(self):
        """Test sanitizing valid labels."""
        label = "Valid Label 123"
        sanitized = InputSanitizer.sanitize_label(label)
        assert sanitized == label

    def test_sanitize_label_invalid_script(self):
        """Test sanitizing labels with script tags."""
        label = "Label <script>alert('xss')</script>"
        
        with pytest.raises(ValueError, match="potentially dangerous content"):
            InputSanitizer.sanitize_label(label)

    def test_sanitize_label_too_long(self):
        """Test sanitizing labels that are too long."""
        label = "x" * (InputSanitizer.MAX_LABEL_LENGTH + 1)
        
        with pytest.raises(ValueError, match="Label too long"):
            InputSanitizer.sanitize_label(label)

    def test_sanitize_element_data_valid(self):
        """Test sanitizing valid element data."""
        element_data = {
            "label": "Test Label",
            "element_type": "node",
            "position": {"x": 100, "y": 200},
            "size": {"width": 120, "height": 60}
        }
        
        sanitized = InputSanitizer.sanitize_element_data(element_data)
        
        assert sanitized["label"] == "Test Label"
        assert sanitized["element_type"] == "node"
        assert sanitized["position"]["x"] == 100
        assert sanitized["position"]["y"] == 200

    def test_sanitize_element_data_invalid_position(self):
        """Test sanitizing element data with invalid position."""
        element_data = {
            "label": "Test",
            "element_type": "node",
            "position": {"x": 99999, "y": 200}  # Out of bounds
        }
        
        with pytest.raises(ValueError, match="Position x out of bounds"):
            InputSanitizer.sanitize_element_data(element_data)

    def test_sanitize_mermaid_code_valid(self):
        """Test sanitizing valid Mermaid code."""
        code = """
        flowchart TD
            A[Start] --> B[End]
        """
        
        sanitized = InputSanitizer.sanitize_mermaid_code(code)
        assert "flowchart TD" in sanitized
        assert "A[Start] --> B[End]" in sanitized

    def test_sanitize_mermaid_code_dangerous(self):
        """Test sanitizing Mermaid code with dangerous content."""
        code = """
        flowchart TD
            A[Start <script>alert('xss')</script>] --> B[End]
        """
        
        with pytest.raises(ValueError, match="potentially dangerous content"):
            InputSanitizer.sanitize_mermaid_code(code)
