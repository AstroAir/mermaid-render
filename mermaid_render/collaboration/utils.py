"""Utility functions for collaboration features."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .activity_log import ActivityLogger, ActivityType
from .collaboration_manager import CollaborationManager, Permission
from .comments import CommentSystem
from .version_control import ChangeSet, VersionControl


def create_collaborative_session(
    diagram_id: str,
    diagram_type: str,
    title: str,
    owner_id: str,
    owner_email: str,
    owner_name: str,
    collaboration_manager: Optional[CollaborationManager] = None,
) -> str:
    """
    Create a new collaborative session for diagram editing.

    This function sets up a new collaborative session that allows multiple users
    to work together on a diagram. The session includes version control, activity
    logging, and permission management.

    Args:
        diagram_id: Unique identifier for the diagram
        diagram_type: Type of diagram (flowchart, sequence, etc.)
        title: Human-readable title for the session
        owner_id: Unique identifier for the session owner
        owner_email: Email address of the session owner
        owner_name: Display name of the session owner
        collaboration_manager: Optional collaboration manager instance

    Returns:
        Session ID for the newly created collaborative session

    Example:
        >>> session_id = create_collaborative_session(
        ...     diagram_id="diagram_123",
        ...     diagram_type="flowchart",
        ...     title="User Registration Flow",
        ...     owner_id="user_456",
        ...     owner_email="alice@example.com",
        ...     owner_name="Alice Smith"
        ... )
    """
    if collaboration_manager is None:
        collaboration_manager = CollaborationManager()

    session = collaboration_manager.create_session(
        diagram_id=diagram_id,
        diagram_type=diagram_type,
        title=title,
        owner_id=owner_id,
        owner_email=owner_email,
        owner_name=owner_name,
    )

    return session.session_id


def invite_collaborator(
    session_id: str,
    user_id: str,
    email: str,
    name: str,
    permission: str = "viewer",
    invited_by: Optional[str] = None,
    collaboration_manager: Optional[CollaborationManager] = None,
) -> bool:
    """
    Invite a collaborator to join a collaborative session.

    Adds a new collaborator to an existing collaborative session with the
    specified permission level. The collaborator will be able to participate
    in diagram editing according to their permission level.

    Args:
        session_id: ID of the collaborative session
        user_id: Unique identifier for the user being invited
        email: Email address of the user being invited
        name: Display name of the user being invited
        permission: Permission level ("viewer", "editor", "admin")
        invited_by: ID of the user sending the invitation
        collaboration_manager: Optional collaboration manager instance

    Returns:
        True if the invitation was successful, False otherwise

    Example:
        >>> success = invite_collaborator(
        ...     session_id="session_123",
        ...     user_id="user_789",
        ...     email="bob@example.com",
        ...     name="Bob Johnson",
        ...     permission="editor",
        ...     invited_by="user_456"
        ... )
    """
    if collaboration_manager is None:
        collaboration_manager = CollaborationManager()

    return collaboration_manager.add_collaborator(
        session_id=session_id,
        user_id=user_id,
        email=email,
        name=name,
        permission=Permission(permission),
        invited_by=invited_by,
    )


def commit_diagram_changes(
    diagram_id: str,
    changes: List[Dict[str, Any]],
    message: str,
    author_id: str,
    author_name: str,
    diagram_data: Dict[str, Any],
    diagram_code: str,
    version_control: Optional[VersionControl] = None,
) -> str:
    """
    Commit changes to diagram version control system.

    Records a set of changes to a diagram in the version control system,
    creating a new commit with the specified message and author information.
    This enables tracking of diagram evolution and rollback capabilities.

    Args:
        diagram_id: Unique identifier for the diagram
        changes: List of change dictionaries describing modifications
        message: Commit message describing the changes
        author_id: Unique identifier for the change author
        author_name: Display name of the change author
        diagram_data: Complete diagram data after changes
        diagram_code: Generated Mermaid code after changes
        version_control: Optional version control instance

    Returns:
        Commit ID for the newly created commit

    Example:
        >>> commit_id = commit_diagram_changes(
        ...     diagram_id="diagram_123",
        ...     changes=[{
        ...         "change_type": "add_node",
        ...         "element_id": "node_1",
        ...         "new_data": {"label": "Start", "shape": "circle"}
        ...     }],
        ...     message="Added start node",
        ...     author_id="user_456",
        ...     author_name="Alice Smith",
        ...     diagram_data={"nodes": [...], "edges": [...]},
        ...     diagram_code="flowchart TD\\n    A[Start]"
        ... )
    """
    if version_control is None:
        version_control = VersionControl(diagram_id)

    # Convert dict changes to ChangeSet objects
    change_sets = []
    for change_dict in changes:
        # Handle timestamp - use current time if not provided
        timestamp = change_dict.get("timestamp")
        if timestamp is None:
            timestamp = datetime.now()

        change_set = ChangeSet(
            change_id=change_dict.get("change_id", ""),
            change_type=change_dict["change_type"],
            element_id=change_dict.get("element_id"),
            element_type=change_dict.get("element_type"),
            old_data=change_dict.get("old_data"),
            new_data=change_dict.get("new_data"),
            timestamp=timestamp,
        )
        change_sets.append(change_set)

    commit = version_control.commit_changes(
        changes=change_sets,
        message=message,
        author_id=author_id,
        author_name=author_name,
        diagram_data=diagram_data,
        diagram_code=diagram_code,
    )

    return commit.commit_id


def create_branch(
    diagram_id: str,
    branch_name: str,
    from_branch: Optional[str] = None,
    created_by: str = "unknown",
    description: str = "",
    version_control: Optional[VersionControl] = None,
) -> str:
    """Create a new branch."""
    if version_control is None:
        version_control = VersionControl(diagram_id)

    branch = version_control.create_branch(
        branch_name=branch_name,
        from_branch=from_branch,
        created_by=created_by,
        description=description,
    )

    return branch.branch_name


def merge_branches(
    diagram_id: str,
    source_branch: str,
    target_branch: str,
    merge_message: str,
    merged_by: str,
    version_control: Optional[VersionControl] = None,
) -> Dict[str, Any]:
    """Merge one branch into another."""
    if version_control is None:
        version_control = VersionControl(diagram_id)

    result = version_control.merge_branches(
        source_branch=source_branch,
        target_branch=target_branch,
        merge_message=merge_message,
        merged_by=merged_by,
    )

    return result.to_dict()


def resolve_conflicts(
    conflicts: List[Dict[str, Any]],
    resolutions: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Resolve merge conflicts."""
    # This is a simplified implementation
    resolved = []

    for conflict in conflicts:
        element_id = conflict["element_id"]
        if element_id in resolutions:
            resolved.append(
                {
                    "element_id": element_id,
                    "resolution_type": resolutions[element_id]["type"],
                    "resolved_value": resolutions[element_id]["value"],
                }
            )

    return resolved


def add_comment(
    author_id: str,
    author_name: str,
    content: str,
    element_id: Optional[str] = None,
    position: Optional[Dict[str, float]] = None,
    parent_comment_id: Optional[str] = None,
    comment_system: Optional[CommentSystem] = None,
) -> str:
    """Add a comment to a diagram."""
    if comment_system is None:
        comment_system = CommentSystem()

    comment = comment_system.add_comment(
        author_id=author_id,
        author_name=author_name,
        content=content,
        element_id=element_id,
        position=position,
        parent_comment_id=parent_comment_id,
    )

    return comment.comment_id


def get_activity_log(
    session_id: str,
    limit: Optional[int] = None,
    activity_type: Optional[str] = None,
    activity_logger: Optional[ActivityLogger] = None,
) -> List[Dict[str, Any]]:
    """Get activity log for a session."""
    if activity_logger is None:
        activity_logger = ActivityLogger()

    activity_type_enum = None
    if activity_type:
        activity_type_enum = ActivityType(activity_type)

    activities = activity_logger.get_session_activities(
        session_id=session_id,
        limit=limit,
        activity_type=activity_type_enum,
    )

    return [activity.to_dict() for activity in activities]
