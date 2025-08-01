"""
Collaborative diagram editing and version control for Mermaid Render.

This package provides comprehensive collaboration features including
multi-user editing, version control, change tracking, conflict resolution,
and integration with Git workflows.

Features:
- Multi-user collaborative editing with real-time synchronization
- Version control with branching and merging capabilities
- Change tracking and history management
- Conflict resolution for simultaneous edits
- Comment and review system
- Integration with Git repositories
- User management and permissions
- Audit trails and activity logs

Example:
    >>> from mermaid_render.collaboration import CollaborationManager, VersionControl
    >>>
    >>> # Setup collaboration
    >>> collab = CollaborationManager()
    >>> version_control = VersionControl()
    >>>
    >>> # Create collaborative session
    >>> session = collab.create_session("my_diagram", "flowchart")
    >>>
    >>> # Add collaborators
    >>> collab.add_collaborator(session.id, "user@example.com", "editor")
    >>>
    >>> # Track changes
    >>> version_control.commit_changes(session.id, "Added new nodes", "user@example.com")
"""

from .activity_log import (
    Activity,
    ActivityLogger,
    ActivityType,
    AuditTrail,
)
from .collaboration_manager import (
    CollaborationManager,
    CollaborativeSession,
    Collaborator,
    Permission,
    SessionState,
)
from .comments import (
    Comment,
    CommentSystem,
    CommentThread,
    Review,
    ReviewStatus,
)
from .diff_engine import (
    Change,
    ChangeType,
    ConflictResolution,
    DiagramDiff,
    DiffEngine,
)
from .merge_resolver import (
    ConflictResolver,
    MergeConflict,
    MergeResolver,
    MergeStrategy,
)

# Convenience functions
from .utils import (
    add_comment,
    commit_diagram_changes,
    create_branch,
    create_collaborative_session,
    get_activity_log,
    invite_collaborator,
    merge_branches,
    resolve_conflicts,
)
from .version_control import (
    Branch,
    ChangeSet,
    Commit,
    DiagramVersion,
    MergeResult,
    VersionControl,
)

__all__ = [
    # Core collaboration
    "CollaborationManager",
    "CollaborativeSession",
    "Collaborator",
    "Permission",
    "SessionState",
    # Version control
    "VersionControl",
    "DiagramVersion",
    "ChangeSet",
    "Commit",
    "Branch",
    "MergeResult",
    # Diff and merge
    "DiffEngine",
    "DiagramDiff",
    "Change",
    "ChangeType",
    "ConflictResolution",
    "MergeResolver",
    "MergeStrategy",
    "ConflictResolver",
    "MergeConflict",
    # Comments and reviews
    "CommentSystem",
    "Comment",
    "CommentThread",
    "Review",
    "ReviewStatus",
    # Activity logging
    "ActivityLogger",
    "Activity",
    "ActivityType",
    "AuditTrail",
    # Utilities
    "create_collaborative_session",
    "invite_collaborator",
    "commit_diagram_changes",
    "create_branch",
    "merge_branches",
    "resolve_conflicts",
    "add_comment",
    "get_activity_log",
]
