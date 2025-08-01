"""
Version control system for collaborative diagram editing.

This module provides Git-like version control capabilities for diagrams
including branching, merging, and change tracking.
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..exceptions import VersionControlError


class MergeStatus(Enum):
    """Status of merge operations."""

    SUCCESS = "success"
    CONFLICT = "conflict"
    FAILED = "failed"


@dataclass
class ChangeSet:
    """Represents a set of changes to a diagram."""

    change_id: str
    change_type: str  # add, modify, delete
    element_id: Optional[str]
    element_type: Optional[str]
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    timestamp: datetime

    def __post_init__(self):
        if not self.change_id:
            self.change_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "change_id": self.change_id,
            "change_type": self.change_type,
            "element_id": self.element_id,
            "element_type": self.element_type,
            "old_data": self.old_data,
            "new_data": self.new_data,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Commit:
    """Represents a commit in the version history."""

    commit_id: str
    parent_commit_id: Optional[str]
    branch_name: str
    author_id: str
    author_name: str
    message: str
    changes: List[ChangeSet]
    timestamp: datetime
    diagram_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.commit_id:
            self.commit_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "commit_id": self.commit_id,
            "parent_commit_id": self.parent_commit_id,
            "branch_name": self.branch_name,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "message": self.message,
            "changes": [c.to_dict() for c in self.changes],
            "timestamp": self.timestamp.isoformat(),
            "diagram_hash": self.diagram_hash,
            "metadata": self.metadata,
        }


@dataclass
class Branch:
    """Represents a branch in the version tree."""

    branch_name: str
    head_commit_id: str
    created_from: Optional[str]
    created_by: str
    created_at: datetime
    description: str = ""
    is_protected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "branch_name": self.branch_name,
            "head_commit_id": self.head_commit_id,
            "created_from": self.created_from,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "is_protected": self.is_protected,
        }


@dataclass
class DiagramVersion:
    """Represents a specific version of a diagram."""

    version_id: str
    commit_id: str
    diagram_data: Dict[str, Any]
    diagram_code: str
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "commit_id": self.commit_id,
            "diagram_data": self.diagram_data,
            "diagram_code": self.diagram_code,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MergeResult:
    """Result of a merge operation."""

    status: MergeStatus
    merge_commit_id: Optional[str]
    conflicts: List[Dict[str, Any]]
    merged_changes: List[ChangeSet]
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "merge_commit_id": self.merge_commit_id,
            "conflicts": self.conflicts,
            "merged_changes": [c.to_dict() for c in self.merged_changes],
            "message": self.message,
        }


class VersionControl:
    """
    Version control system for diagrams.

    Provides Git-like functionality for tracking changes, branching,
    and merging diagram modifications.
    """

    def __init__(self, diagram_id: str):
        """
        Initialize version control for a diagram.

        Args:
            diagram_id: Unique diagram identifier
        """
        self.diagram_id = diagram_id
        self.commits: Dict[str, Commit] = {}
        self.branches: Dict[str, Branch] = {}
        self.versions: Dict[str, DiagramVersion] = {}
        self.current_branch = "main"

        # Create initial main branch
        self._create_initial_branch()

    def _create_initial_branch(self) -> None:
        """Create the initial main branch."""
        self.branches["main"] = Branch(
            branch_name="main",
            head_commit_id="",
            created_from=None,
            created_by="system",
            created_at=datetime.now(),
            description="Main branch",
            is_protected=True,
        )

    def commit_changes(
        self,
        changes: List[ChangeSet],
        message: str,
        author_id: str,
        author_name: str,
        diagram_data: Dict[str, Any],
        diagram_code: str,
        branch_name: Optional[str] = None,
    ) -> Commit:
        """
        Commit changes to the version history.

        Args:
            changes: List of changes to commit
            message: Commit message
            author_id: Author user ID
            author_name: Author name
            diagram_data: Current diagram data
            diagram_code: Current diagram code
            branch_name: Target branch (default: current branch)

        Returns:
            Created commit
        """
        if branch_name is None:
            branch_name = self.current_branch

        if branch_name not in self.branches:
            raise VersionControlError(f"Branch '{branch_name}' does not exist")

        branch = self.branches[branch_name]

        # Calculate diagram hash
        diagram_hash = self._calculate_diagram_hash(diagram_data)

        # Create commit
        commit = Commit(
            commit_id=str(uuid.uuid4()),
            parent_commit_id=branch.head_commit_id if branch.head_commit_id else None,
            branch_name=branch_name,
            author_id=author_id,
            author_name=author_name,
            message=message,
            changes=changes,
            timestamp=datetime.now(),
            diagram_hash=diagram_hash,
        )

        # Store commit
        self.commits[commit.commit_id] = commit

        # Update branch head
        branch.head_commit_id = commit.commit_id

        # Create version
        version = DiagramVersion(
            version_id=str(uuid.uuid4()),
            commit_id=commit.commit_id,
            diagram_data=diagram_data,
            diagram_code=diagram_code,
            created_at=commit.timestamp,
        )

        self.versions[version.version_id] = version

        return commit

    def create_branch(
        self,
        branch_name: str,
        from_branch: Optional[str] = None,
        from_commit: Optional[str] = None,
        created_by: str = "unknown",
        description: str = "",
    ) -> Branch:
        """
        Create a new branch.

        Args:
            branch_name: Name of new branch
            from_branch: Source branch (default: current branch)
            from_commit: Specific commit to branch from
            created_by: User creating the branch
            description: Branch description

        Returns:
            Created branch
        """
        if branch_name in self.branches:
            raise VersionControlError(f"Branch '{branch_name}' already exists")

        # Determine source commit
        if from_commit:
            if from_commit not in self.commits:
                raise VersionControlError(f"Commit '{from_commit}' does not exist")
            head_commit_id = from_commit
            created_from = from_commit
        else:
            source_branch_name = from_branch or self.current_branch
            if source_branch_name not in self.branches:
                raise VersionControlError(
                    f"Source branch '{source_branch_name}' does not exist"
                )

            source_branch = self.branches[source_branch_name]
            head_commit_id = source_branch.head_commit_id
            created_from = source_branch_name

        # Create branch
        branch = Branch(
            branch_name=branch_name,
            head_commit_id=head_commit_id,
            created_from=created_from,
            created_by=created_by,
            created_at=datetime.now(),
            description=description,
        )

        self.branches[branch_name] = branch
        return branch

    def merge_branches(
        self,
        source_branch: str,
        target_branch: str,
        merge_message: str,
        merged_by: str,
        strategy: str = "auto",
    ) -> MergeResult:
        """
        Merge one branch into another.

        Args:
            source_branch: Branch to merge from
            target_branch: Branch to merge into
            merge_message: Merge commit message
            merged_by: User performing the merge
            strategy: Merge strategy

        Returns:
            Merge result
        """
        if source_branch not in self.branches:
            raise VersionControlError(f"Source branch '{source_branch}' does not exist")

        if target_branch not in self.branches:
            raise VersionControlError(f"Target branch '{target_branch}' does not exist")

        source = self.branches[source_branch]
        target = self.branches[target_branch]

        # Get commits to merge
        source_commits = self._get_branch_commits(source_branch)
        target_commits = self._get_branch_commits(target_branch)

        # Find common ancestor
        common_ancestor = self._find_common_ancestor(source_commits, target_commits)

        # Get changes since common ancestor
        source_changes = self._get_changes_since_commit(source_branch, common_ancestor)
        target_changes = self._get_changes_since_commit(target_branch, common_ancestor)

        # Detect conflicts
        conflicts = self._detect_conflicts(source_changes, target_changes)

        if conflicts:
            return MergeResult(
                status=MergeStatus.CONFLICT,
                merge_commit_id=None,
                conflicts=conflicts,
                merged_changes=[],
                message="Merge conflicts detected",
            )

        # Perform merge
        merged_changes = source_changes + target_changes

        # Create merge commit
        merge_commit = Commit(
            commit_id=str(uuid.uuid4()),
            parent_commit_id=target.head_commit_id,
            branch_name=target_branch,
            author_id=merged_by,
            author_name=merged_by,
            message=merge_message,
            changes=merged_changes,
            timestamp=datetime.now(),
            diagram_hash="",  # Would be calculated from merged state
            metadata={"merge_from": source_branch, "merge_type": strategy},
        )

        self.commits[merge_commit.commit_id] = merge_commit
        target.head_commit_id = merge_commit.commit_id

        return MergeResult(
            status=MergeStatus.SUCCESS,
            merge_commit_id=merge_commit.commit_id,
            conflicts=[],
            merged_changes=merged_changes,
            message="Merge completed successfully",
        )

    def get_commit_history(
        self,
        branch_name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Commit]:
        """
        Get commit history for a branch.

        Args:
            branch_name: Branch name (default: current branch)
            limit: Maximum number of commits to return

        Returns:
            List of commits in chronological order
        """
        if branch_name is None:
            branch_name = self.current_branch

        if branch_name not in self.branches:
            raise VersionControlError(f"Branch '{branch_name}' does not exist")

        commits = self._get_branch_commits(branch_name)

        # Sort by timestamp (newest first)
        commits.sort(key=lambda c: c.timestamp, reverse=True)

        if limit:
            commits = commits[:limit]

        return commits

    def get_version(self, commit_id: str) -> Optional[DiagramVersion]:
        """Get diagram version for a specific commit."""
        for version in self.versions.values():
            if version.commit_id == commit_id:
                return version
        return None

    def get_diff(self, commit1_id: str, commit2_id: str) -> List[ChangeSet]:
        """Get differences between two commits."""
        if commit1_id not in self.commits or commit2_id not in self.commits:
            raise VersionControlError("One or both commits do not exist")

        # This is a simplified implementation
        # In practice, you'd need to reconstruct the diagram state at each commit
        # and compute the actual differences

        commit1 = self.commits[commit1_id]
        commit2 = self.commits[commit2_id]

        # Return changes from commit2 (assuming it's newer)
        return commit2.changes

    def _calculate_diagram_hash(self, diagram_data: Dict[str, Any]) -> str:
        """Calculate hash of diagram data."""
        import json

        diagram_json = json.dumps(diagram_data, sort_keys=True)
        return hashlib.sha256(diagram_json.encode()).hexdigest()

    def _get_branch_commits(self, branch_name: str) -> List[Commit]:
        """Get all commits in a branch."""
        if branch_name not in self.branches:
            return []

        branch = self.branches[branch_name]
        commits = []
        current_commit_id = branch.head_commit_id

        while current_commit_id and current_commit_id in self.commits:
            commit = self.commits[current_commit_id]
            commits.append(commit)
            current_commit_id = commit.parent_commit_id

        return commits

    def _find_common_ancestor(
        self,
        commits1: List[Commit],
        commits2: List[Commit],
    ) -> Optional[str]:
        """Find common ancestor of two commit lists."""
        commit_ids1 = {c.commit_id for c in commits1}

        for commit in commits2:
            if commit.commit_id in commit_ids1:
                return commit.commit_id

        return None

    def _get_changes_since_commit(
        self,
        branch_name: str,
        since_commit_id: Optional[str],
    ) -> List[ChangeSet]:
        """Get all changes in a branch since a specific commit."""
        commits = self._get_branch_commits(branch_name)
        changes = []

        for commit in commits:
            if commit.commit_id == since_commit_id:
                break
            changes.extend(commit.changes)

        return changes

    def _detect_conflicts(
        self,
        changes1: List[ChangeSet],
        changes2: List[ChangeSet],
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between two sets of changes."""
        conflicts = []

        # Group changes by element ID
        elements1 = {}
        elements2 = {}

        for change in changes1:
            if change.element_id:
                elements1[change.element_id] = change

        for change in changes2:
            if change.element_id:
                elements2[change.element_id] = change

        # Check for conflicts
        for element_id in elements1:
            if element_id in elements2:
                change1 = elements1[element_id]
                change2 = elements2[element_id]

                # Conflict if both modify the same element
                if change1.change_type == "modify" and change2.change_type == "modify":
                    conflicts.append(
                        {
                            "element_id": element_id,
                            "conflict_type": "modify_modify",
                            "change1": change1.to_dict(),
                            "change2": change2.to_dict(),
                        }
                    )

        return conflicts
