"""
Diagram element classes for the interactive diagram builder.

This module provides the core data classes for representing
diagram elements and connections.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ...exceptions import DiagramError
from .enums import ElementType
from .geometry import Position, Size


@dataclass
class DiagramElement:
    """
    Represents a visual element in the diagram builder.

    Provides a visual representation of diagram components with
    position, styling, and interaction capabilities.
    """

    element_type: ElementType
    position: Position
    size: Size
    label: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    properties: dict[str, Any] = field(default_factory=dict)
    style: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate element after initialization."""
        if not self.label or not self.label.strip():
            raise DiagramError("Element label cannot be empty")

    def update_position(self, x: float, y: float) -> None:
        """Update element position."""
        self.position.x = x
        self.position.y = y
        self.updated_at = datetime.now()

    def update_size(self, width: float, height: float) -> None:
        """Update element size."""
        self.size.width = width
        self.size.height = height
        self.updated_at = datetime.now()

    def update_properties(self, properties: dict[str, Any]) -> None:
        """Update element properties."""
        self.properties.update(properties)
        self.updated_at = datetime.now()

    def update_style(self, style: dict[str, Any]) -> None:
        """Update element styling."""
        self.style.update(style)
        self.updated_at = datetime.now()

    def move(self, position: Position) -> None:
        """Move element to new position."""
        self.position = position
        self.updated_at = datetime.now()

    def resize(self, size: Size) -> None:
        """Resize element to new dimensions."""
        self.size = size
        self.updated_at = datetime.now()

    def bounds(self) -> dict[str, float]:
        """Get element bounds as dictionary."""
        return {
            "left": self.position.x,
            "top": self.position.y,
            "right": self.position.x + self.size.width,
            "bottom": self.position.y + self.size.height,
        }

    def contains_point(self, position: Position) -> bool:
        """Check if point is within element bounds."""
        return (
            self.position.x <= position.x <= self.position.x + self.size.width
            and self.position.y <= position.y <= self.position.y + self.size.height
        )

    def overlaps_with(self, other: "DiagramElement") -> bool:
        """Check if this element overlaps with another."""
        bounds1 = self.bounds()
        bounds2 = other.bounds()

        return not (
            bounds1["right"] < bounds2["left"]
            or bounds2["right"] < bounds1["left"]
            or bounds1["bottom"] < bounds2["top"]
            or bounds2["bottom"] < bounds1["top"]
        )

    def clone(self) -> "DiagramElement":
        """Create a copy of this element with a new ID."""
        return DiagramElement(
            element_type=self.element_type,
            position=Position(self.position.x, self.position.y),
            size=Size(self.size.width, self.size.height),
            label=self.label,
            properties=self.properties.copy(),
            style=self.style.copy(),
            metadata=self.metadata.copy(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "element_type": self.element_type.value,
            "label": self.label,
            "position": self.position.to_dict(),
            "size": self.size.to_dict(),
            "properties": self.properties,
            "style": self.style,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DiagramElement":
        """Create from dictionary."""
        created_at = datetime.now()
        updated_at = datetime.now()

        if "created_at" in data:
            created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            updated_at = datetime.fromisoformat(data["updated_at"])

        return cls(
            element_type=ElementType(data["element_type"]),
            position=Position.from_dict(data["position"]),
            size=Size.from_dict(data["size"]),
            label=data["label"],
            id=data.get("id", str(uuid.uuid4())),
            properties=data.get("properties", {}),
            style=data.get("style", {}),
            metadata=data.get("metadata", {}),
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class DiagramConnection:
    """
    Represents a connection between diagram elements.

    Provides visual and logical connections between elements
    with styling and labeling capabilities.
    """

    id: str
    source_id: str
    target_id: str
    label: str = ""
    connection_type: str = "default"
    style: dict[str, Any] = field(default_factory=dict)
    properties: dict[str, Any] = field(default_factory=dict)
    control_points: list[Position] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())

    def update_label(self, label: str) -> None:
        """Update connection label."""
        self.label = label
        self.updated_at = datetime.now()

    def update_style(self, style: dict[str, Any]) -> None:
        """Update connection styling."""
        self.style.update(style)
        self.updated_at = datetime.now()

    def add_control_point(self, position: Position) -> None:
        """Add control point for connection routing."""
        self.control_points.append(position)
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "label": self.label,
            "connection_type": self.connection_type,
            "style": self.style,
            "properties": self.properties,
            "control_points": [cp.to_dict() for cp in self.control_points],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DiagramConnection":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            label=data.get("label", ""),
            connection_type=data.get("connection_type", "default"),
            style=data.get("style", {}),
            properties=data.get("properties", {}),
            control_points=[
                Position.from_dict(cp) for cp in data.get("control_points", [])
            ],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
