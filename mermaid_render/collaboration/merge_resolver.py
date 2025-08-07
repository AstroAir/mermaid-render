"""Merge conflict resolution for collaborative editing."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .diff_engine import Change, ChangeType, ConflictResolution


class MergeStrategy(Enum):
    """Strategies for resolving merge conflicts."""

    AUTO = "auto"
    MANUAL = "manual"
    PREFER_SOURCE = "prefer_source"
    PREFER_TARGET = "prefer_target"


@dataclass
class MergeConflict:
    """Represents a merge conflict."""

    element_id: str
    conflict_type: str
    source_change: Change
    target_change: Change
    suggested_resolution: Optional[ConflictResolution] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "conflict_type": self.conflict_type,
            "source_change": self.source_change.to_dict(),
            "target_change": self.target_change.to_dict(),
            "suggested_resolution": (
                self.suggested_resolution.to_dict()
                if self.suggested_resolution
                else None
            ),
        }


class ConflictResolver:
    """Resolves merge conflicts between diagram versions."""

    def detect_conflicts(
        self,
        source_changes: List[Change],
        target_changes: List[Change],
    ) -> List[MergeConflict]:
        """Detect conflicts between two sets of changes."""
        conflicts = []

        # Group changes by element ID
        source_by_element = {c.element_id: c for c in source_changes}
        target_by_element = {c.element_id: c for c in target_changes}

        # Find conflicting elements
        for element_id in source_by_element:
            if element_id in target_by_element:
                source_change = source_by_element[element_id]
                target_change = target_by_element[element_id]

                conflict_type = self._determine_conflict_type(
                    source_change, target_change
                )
                if conflict_type:
                    conflict = MergeConflict(
                        element_id=element_id,
                        conflict_type=conflict_type,
                        source_change=source_change,
                        target_change=target_change,
                    )
                    conflicts.append(conflict)

        return conflicts

    def resolve_conflicts(
        self,
        conflicts: List[MergeConflict],
        strategy: MergeStrategy = MergeStrategy.AUTO,
        manual_resolutions: Optional[Dict[str, ConflictResolution]] = None,
    ) -> List[ConflictResolution]:
        """Resolve merge conflicts using specified strategy."""
        resolutions = []

        for conflict in conflicts:
            if manual_resolutions and conflict.element_id in manual_resolutions:
                # Use manual resolution
                resolutions.append(manual_resolutions[conflict.element_id])
            else:
                # Use automatic resolution
                resolution = self._auto_resolve_conflict(conflict, strategy)
                if resolution:
                    resolutions.append(resolution)

        return resolutions

    def _determine_conflict_type(
        self, change1: Change, change2: Change
    ) -> Optional[str]:
        """Determine the type of conflict between two changes."""
        if (
            change1.change_type == ChangeType.MODIFY
            and change2.change_type == ChangeType.MODIFY
        ):
            return "modify_modify"
        elif (
            change1.change_type == ChangeType.DELETE
            and change2.change_type == ChangeType.MODIFY
        ):
            return "delete_modify"
        elif (
            change1.change_type == ChangeType.MODIFY
            and change2.change_type == ChangeType.DELETE
        ):
            return "modify_delete"
        elif (
            change1.change_type == ChangeType.DELETE
            and change2.change_type == ChangeType.DELETE
        ):
            return "delete_delete"

        return None

    def _auto_resolve_conflict(
        self,
        conflict: MergeConflict,
        strategy: MergeStrategy,
    ) -> Optional[ConflictResolution]:
        """Automatically resolve a conflict using the specified strategy."""
        if strategy == MergeStrategy.PREFER_SOURCE:
            return ConflictResolution(
                element_id=conflict.element_id,
                resolution_type="keep_source",
                resolved_value=conflict.source_change.new_value,
            )
        elif strategy == MergeStrategy.PREFER_TARGET:
            return ConflictResolution(
                element_id=conflict.element_id,
                resolution_type="keep_target",
                resolved_value=conflict.target_change.new_value,
            )
        elif strategy == MergeStrategy.AUTO:
            # Simple auto-resolution logic
            if conflict.conflict_type == "modify_modify":
                # Prefer the most recent change (target)
                return ConflictResolution(
                    element_id=conflict.element_id,
                    resolution_type="keep_target",
                    resolved_value=conflict.target_change.new_value,
                )

        return None


class MergeResolver:
    """High-level merge resolver for diagram collaboration."""

    def __init__(self) -> None:
        self.conflict_resolver = ConflictResolver()

    def merge_changes(
        self,
        base_diagram: Dict[str, Any],
        source_changes: List[Change],
        target_changes: List[Change],
        strategy: MergeStrategy = MergeStrategy.AUTO,
    ) -> Dict[str, Any]:
        """Merge changes from two branches."""
        # Detect conflicts
        conflicts = self.conflict_resolver.detect_conflicts(
            source_changes, target_changes
        )

        if conflicts:
            # Resolve conflicts
            resolutions = self.conflict_resolver.resolve_conflicts(conflicts, strategy)

            # Apply resolutions
            merged_diagram = self._apply_resolutions(base_diagram, resolutions)
        else:
            # No conflicts, apply all changes
            merged_diagram = self._apply_changes(
                base_diagram, source_changes + target_changes
            )

        return merged_diagram

    def _apply_changes(
        self, diagram: Dict[str, Any], changes: List[Change]
    ) -> Dict[str, Any]:
        """Apply a list of changes to a diagram."""
        result = diagram.copy()

        for change in changes:
            if change.change_type == ChangeType.ADD:
                if "elements" not in result:
                    result["elements"] = {}
                result["elements"][change.element_id] = change.new_value
            elif change.change_type == ChangeType.MODIFY:
                if "elements" in result and change.element_id in result["elements"]:
                    result["elements"][change.element_id] = change.new_value
            elif change.change_type == ChangeType.DELETE:
                if "elements" in result and change.element_id in result["elements"]:
                    del result["elements"][change.element_id]

        return result

    def _apply_resolutions(
        self,
        diagram: Dict[str, Any],
        resolutions: List[ConflictResolution],
    ) -> Dict[str, Any]:
        """Apply conflict resolutions to a diagram."""
        result = diagram.copy()

        for resolution in resolutions:
            if resolution.resolution_type in ["keep_source", "keep_target", "merge"]:
                if "elements" not in result:
                    result["elements"] = {}
                result["elements"][resolution.element_id] = resolution.resolved_value

        return result
