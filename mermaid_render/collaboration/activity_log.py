"""Activity logging and audit trail for collaboration."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ActivityType(Enum):
    """Types of activities in collaborative editing."""

    SESSION_CREATED = "session_created"
    COLLABORATOR_JOINED = "collaborator_joined"
    COLLABORATOR_LEFT = "collaborator_left"
    ELEMENT_ADDED = "element_added"
    ELEMENT_MODIFIED = "element_modified"
    ELEMENT_DELETED = "element_deleted"
    CONNECTION_ADDED = "connection_added"
    CONNECTION_MODIFIED = "connection_modified"
    CONNECTION_DELETED = "connection_deleted"
    COMMENT_ADDED = "comment_added"
    COMMENT_RESOLVED = "comment_resolved"
    REVIEW_CREATED = "review_created"
    REVIEW_UPDATED = "review_updated"
    COMMIT_CREATED = "commit_created"
    BRANCH_CREATED = "branch_created"
    MERGE_COMPLETED = "merge_completed"
    PERMISSION_CHANGED = "permission_changed"


@dataclass
class Activity:
    """Represents an activity in the collaboration system."""

    activity_id: str
    activity_type: ActivityType
    user_id: str
    user_name: str
    session_id: str
    timestamp: datetime
    details: Dict[str, Any]
    metadata: Dict[str, Any]

    def __post_init__(self) -> None:
        if not self.activity_id:
            self.activity_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activity_id": self.activity_id,
            "activity_type": self.activity_type.value,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "metadata": self.metadata,
        }


@dataclass
class AuditTrail:
    """Represents an audit trail for a session."""

    session_id: str
    activities: List[Activity]
    created_at: datetime

    def add_activity(self, activity: Activity) -> None:
        self.activities.append(activity)

    def get_activities_by_type(self, activity_type: ActivityType) -> List[Activity]:
        return [a for a in self.activities if a.activity_type == activity_type]

    def get_activities_by_user(self, user_id: str) -> List[Activity]:
        return [a for a in self.activities if a.user_id == user_id]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "activities": [a.to_dict() for a in self.activities],
            "created_at": self.created_at.isoformat(),
        }


class ActivityLogger:
    """Logs and manages activities for collaborative editing."""

    def __init__(self) -> None:
        self.activities: Dict[str, Activity] = {}
        self.audit_trails: Dict[str, AuditTrail] = {}

    def log_activity(
        self,
        activity_type: ActivityType,
        user_id: str,
        user_name: str,
        session_id: str,
        details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Activity:
        """Log a new activity."""
        activity = Activity(
            activity_id=str(uuid.uuid4()),
            activity_type=activity_type,
            user_id=user_id,
            user_name=user_name,
            session_id=session_id,
            timestamp=datetime.now(),
            details=details,
            metadata=metadata or {},
        )

        self.activities[activity.activity_id] = activity

        # Add to audit trail
        if session_id not in self.audit_trails:
            self.audit_trails[session_id] = AuditTrail(
                session_id=session_id,
                activities=[],
                created_at=datetime.now(),
            )

        self.audit_trails[session_id].add_activity(activity)

        return activity

    def get_session_activities(
        self,
        session_id: str,
        limit: Optional[int] = None,
        activity_type: Optional[ActivityType] = None,
    ) -> List[Activity]:
        """Get activities for a session."""
        if session_id not in self.audit_trails:
            return []

        activities = self.audit_trails[session_id].activities

        if activity_type:
            activities = [a for a in activities if a.activity_type == activity_type]

        # Sort by timestamp (newest first)
        activities.sort(key=lambda a: a.timestamp, reverse=True)

        if limit:
            activities = activities[:limit]

        return activities

    def get_user_activities(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Activity]:
        """Get activities for a user."""
        activities: List[Activity] = []

        if session_id:
            # Get activities for specific session
            if session_id in self.audit_trails:
                activities = self.audit_trails[session_id].get_activities_by_user(
                    user_id
                )
        else:
            # Get activities across all sessions
            for audit_trail in self.audit_trails.values():
                activities.extend(audit_trail.get_activities_by_user(user_id))

        # Sort by timestamp (newest first)
        activities.sort(key=lambda a: a.timestamp, reverse=True)

        if limit:
            activities = activities[:limit]

        return activities

    def get_activities_by_user(self, user_id: str) -> List[Activity]:
        """Get all activities for a specific user across all sessions."""
        return self.get_user_activities(user_id)

    def get_activities_by_type(self, activity_type: ActivityType) -> List[Activity]:
        """Get all activities of a specific type across all sessions."""
        activities: List[Activity] = []
        for audit_trail in self.audit_trails.values():
            activities.extend(audit_trail.get_activities_by_type(activity_type))

        # Sort by timestamp (newest first)
        activities.sort(key=lambda a: a.timestamp, reverse=True)
        return activities

    def get_activity_summary(self, session_id: str) -> Dict[str, Any]:
        """Get activity summary for a session."""
        if session_id not in self.audit_trails:
            return {}

        activities = self.audit_trails[session_id].activities

        # Count activities by type
        activity_counts: Dict[str, int] = {}
        for activity in activities:
            activity_type = activity.activity_type.value
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1

        # Count activities by user
        user_counts: Dict[str, int] = {}
        for activity in activities:
            user_id = activity.user_id
            user_counts[user_id] = user_counts.get(user_id, 0) + 1

        # Get time range
        if activities:
            first_activity = min(activities, key=lambda a: a.timestamp)
            last_activity = max(activities, key=lambda a: a.timestamp)
            time_range: Optional[Dict[str, str]] = {
                "start": first_activity.timestamp.isoformat(),
                "end": last_activity.timestamp.isoformat(),
            }
        else:
            time_range = None

        return {
            "session_id": session_id,
            "total_activities": len(activities),
            "activity_counts": activity_counts,
            "user_counts": user_counts,
            "time_range": time_range,
        }
