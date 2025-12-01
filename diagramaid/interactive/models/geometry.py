"""
Geometry classes for the interactive diagram builder.

This module provides position and size data classes for
representing visual element geometry.
"""

from dataclasses import dataclass


@dataclass
class Position:
    """2D position for visual elements."""

    x: float
    y: float

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> "Position":
        return cls(x=data["x"], y=data["y"])

    def distance_to(self, other: "Position") -> float:
        """Calculate distance to another position."""
        import math

        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def move(self, dx: float, dy: float) -> "Position":
        """Create a new position moved by the given offsets."""
        return Position(self.x + dx, self.y + dy)


@dataclass
class Size:
    """Size dimensions for visual elements."""

    width: float
    height: float

    def __post_init__(self) -> None:
        """Validate size dimensions."""
        if self.width <= 0:
            raise ValueError("Width must be positive")
        if self.height <= 0:
            raise ValueError("Height must be positive")

    def to_dict(self) -> dict[str, float]:
        return {"width": self.width, "height": self.height}

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> "Size":
        return cls(width=data["width"], height=data["height"])

    def area(self) -> float:
        """Calculate the area of the size."""
        return self.width * self.height

    def aspect_ratio(self) -> float:
        """Calculate the aspect ratio (width/height)."""
        return self.width / self.height

    def scale(self, factor: float) -> "Size":
        """Create a new size scaled by the given factor."""
        return Size(self.width * factor, self.height * factor)
