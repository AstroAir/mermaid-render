"""Diff engine for comparing diagram versions."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class ChangeType(Enum):
    """Types of changes in diagrams."""

    ADD = "add"
    MODIFY = "modify"
    DELETE = "delete"
    MOVE = "move"


@dataclass
class Change:
    """Represents a single change in a diagram."""

    change_type: ChangeType
    element_id: str
    element_type: str
    old_value: Any = None
    new_value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_type": self.change_type.value,
            "element_id": self.element_id,
            "element_type": self.element_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }


@dataclass
class DiagramDiff:
    """Represents differences between two diagrams."""

    changes: List[Change]
    summary: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "changes": [c.to_dict() for c in self.changes],
            "summary": self.summary,
        }


@dataclass
class ConflictResolution:
    """Represents resolution for a merge conflict."""

    element_id: str
    resolution_type: str  # "keep_source", "keep_target", "merge"
    resolved_value: Any

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "resolution_type": self.resolution_type,
            "resolved_value": self.resolved_value,
        }


class DiffEngine:
    """Engine for computing differences between diagrams."""

    def compute_diff(
        self,
        diagram1: Dict[str, Any],
        diagram2: Dict[str, Any],
    ) -> DiagramDiff:
        """Compute differences between two diagrams."""
        changes = []

        # Compare elements
        elements1 = diagram1.get("elements", {})
        elements2 = diagram2.get("elements", {})

        # Find added elements
        for elem_id in elements2:
            if elem_id not in elements1:
                changes.append(
                    Change(
                        change_type=ChangeType.ADD,
                        element_id=elem_id,
                        element_type=elements2[elem_id].get("element_type", "unknown"),
                        new_value=elements2[elem_id],
                    )
                )

        # Find deleted elements
        for elem_id in elements1:
            if elem_id not in elements2:
                changes.append(
                    Change(
                        change_type=ChangeType.DELETE,
                        element_id=elem_id,
                        element_type=elements1[elem_id].get("element_type", "unknown"),
                        old_value=elements1[elem_id],
                    )
                )

        # Find modified elements
        for elem_id in elements1:
            if elem_id in elements2:
                if elements1[elem_id] != elements2[elem_id]:
                    changes.append(
                        Change(
                            change_type=ChangeType.MODIFY,
                            element_id=elem_id,
                            element_type=elements1[elem_id].get(
                                "element_type", "unknown"
                            ),
                            old_value=elements1[elem_id],
                            new_value=elements2[elem_id],
                        )
                    )

        # Calculate summary
        summary = {
            "added": sum(1 for c in changes if c.change_type == ChangeType.ADD),
            "modified": sum(1 for c in changes if c.change_type == ChangeType.MODIFY),
            "deleted": sum(1 for c in changes if c.change_type == ChangeType.DELETE),
            "total": len(changes),
        }

        return DiagramDiff(changes=changes, summary=summary)
