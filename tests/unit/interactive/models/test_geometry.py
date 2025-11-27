"""
Unit tests for interactive.models.geometry module.

Tests the Position and Size classes.
"""

import pytest

from mermaid_render.interactive.models.geometry import Position, Size


@pytest.mark.unit
class TestPosition:
    """Unit tests for Position class."""

    def test_initialization(self) -> None:
        """Test Position initialization."""
        pos = Position(10.5, 20.3)
        assert pos.x == 10.5
        assert pos.y == 20.3

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        pos = Position(10, 20)
        result = pos.to_dict()
        assert result == {"x": 10, "y": 20}

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        data = {"x": 15, "y": 25}
        pos = Position.from_dict(data)
        assert pos.x == 15
        assert pos.y == 25

    def test_equality(self) -> None:
        """Test position equality."""
        pos1 = Position(10, 20)
        pos2 = Position(10, 20)
        pos3 = Position(10, 21)
        assert pos1 == pos2
        assert pos1 != pos3

    def test_distance_to(self) -> None:
        """Test distance calculation."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        assert pos1.distance_to(pos2) == 5.0

    def test_move(self) -> None:
        """Test moving position."""
        pos = Position(10, 20)
        new_pos = pos.move(5, -3)
        assert new_pos.x == 15
        assert new_pos.y == 17
        # Original unchanged
        assert pos.x == 10
        assert pos.y == 20


@pytest.mark.unit
class TestSize:
    """Unit tests for Size class."""

    def test_initialization(self) -> None:
        """Test Size initialization."""
        size = Size(100, 50)
        assert size.width == 100
        assert size.height == 50

    def test_negative_width_raises(self) -> None:
        """Test that negative width raises error."""
        with pytest.raises(ValueError):
            Size(-10, 50)

    def test_negative_height_raises(self) -> None:
        """Test that negative height raises error."""
        with pytest.raises(ValueError):
            Size(100, -20)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        size = Size(100, 50)
        result = size.to_dict()
        assert result == {"width": 100, "height": 50}

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        data = {"width": 120, "height": 80}
        size = Size.from_dict(data)
        assert size.width == 120
        assert size.height == 80

    def test_area(self) -> None:
        """Test area calculation."""
        size = Size(10, 20)
        assert size.area() == 200

    def test_aspect_ratio(self) -> None:
        """Test aspect ratio calculation."""
        size = Size(16, 9)
        assert abs(size.aspect_ratio() - 16/9) < 0.001

    def test_scale(self) -> None:
        """Test scaling size."""
        size = Size(100, 50)
        scaled = size.scale(2.0)
        assert scaled.width == 200
        assert scaled.height == 100
