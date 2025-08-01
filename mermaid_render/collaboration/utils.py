"""Utility functions for collaboration features."""

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
    """Create a new collaborative session."""
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
    """Invite a collaborator to a session."""
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
    """Commit changes to diagram version control."""
    if version_control is None:
        version_control = VersionControl(diagram_id)

    # Convert dict changes to ChangeSet objects
    change_sets = []
    for change_dict in changes:
        change_set = ChangeSet(
            change_id=change_dict.get("change_id", ""),
            change_type=change_dict["change_type"],
            element_id=change_dict.get("element_id"),
            element_type=change_dict.get("element_type"),
            old_data=change_dict.get("old_data"),
            new_data=change_dict.get("new_data"),
            timestamp=change_dict.get("timestamp"),
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
