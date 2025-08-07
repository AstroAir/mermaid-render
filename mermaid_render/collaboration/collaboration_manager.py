"""
Core collaboration management for multi-user diagram editing.

This module provides the main collaboration functionality including
session management, user coordination, and real-time synchronization.
"""

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class Permission(Enum):
    """User permissions for collaborative sessions."""

    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    COMMENTER = "commenter"


class SessionState(Enum):
    """States of collaborative sessions."""

    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    LOCKED = "locked"


@dataclass
class Collaborator:
    """Represents a collaborator in a session."""

    user_id: str
    email: str
    name: str
    permission: Permission
    joined_at: datetime
    last_active: datetime
    is_online: bool = False
    cursor_position: Optional[Dict[str, Any]] = None
    selection: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.selection is None:
            self.selection = []

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_active = datetime.now()

    def set_online(self, online: bool) -> None:
        """Set online status."""
        self.is_online = online
        if online:
            self.update_activity()

    def update_cursor(self, position: Dict[str, Any]) -> None:
        """Update cursor position."""
        self.cursor_position = position
        self.update_activity()

    def update_selection(self, selection: List[str]) -> None:
        """Update selected elements."""
        self.selection = selection
        self.update_activity()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "permission": self.permission.value,
            "joined_at": self.joined_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "is_online": self.is_online,
            "cursor_position": self.cursor_position,
            "selection": self.selection,
        }


@dataclass
class CollaborativeSession:
    """Represents a collaborative editing session."""

    session_id: str
    diagram_id: str
    diagram_type: str
    title: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    state: SessionState
    collaborators: Dict[str, Collaborator] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_collaborator(self, collaborator: Collaborator) -> None:
        """Add collaborator to session."""
        self.collaborators[collaborator.user_id] = collaborator
        self.updated_at = datetime.now()

    def remove_collaborator(self, user_id: str) -> bool:
        """Remove collaborator from session."""
        if user_id in self.collaborators and user_id != self.owner_id:
            del self.collaborators[user_id]
            self.updated_at = datetime.now()
            return True
        return False

    def get_collaborator(self, user_id: str) -> Optional[Collaborator]:
        """Get collaborator by user ID."""
        return self.collaborators.get(user_id)

    def update_collaborator_permission(
        self, user_id: str, permission: Permission
    ) -> bool:
        """Update collaborator permission."""
        if user_id in self.collaborators and user_id != self.owner_id:
            self.collaborators[user_id].permission = permission
            self.updated_at = datetime.now()
            return True
        return False

    def get_online_collaborators(self) -> List[Collaborator]:
        """Get list of online collaborators."""
        return [c for c in self.collaborators.values() if c.is_online]

    def can_edit(self, user_id: str) -> bool:
        """Check if user can edit the diagram."""
        collaborator = self.get_collaborator(user_id)
        if not collaborator:
            return False
        return collaborator.permission in [Permission.OWNER, Permission.EDITOR]

    def can_comment(self, user_id: str) -> bool:
        """Check if user can add comments."""
        collaborator = self.get_collaborator(user_id)
        if not collaborator:
            return False
        return collaborator.permission in [
            Permission.OWNER,
            Permission.EDITOR,
            Permission.COMMENTER,
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "diagram_id": self.diagram_id,
            "diagram_type": self.diagram_type,
            "title": self.title,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "state": self.state.value,
            "collaborators": {
                uid: c.to_dict() for uid, c in self.collaborators.items()
            },
            "settings": self.settings,
            "metadata": self.metadata,
        }


class CollaborationManager:
    """
    Manages collaborative diagram editing sessions.

    Provides functionality for creating sessions, managing collaborators,
    coordinating real-time updates, and handling permissions.
    """

    def __init__(self) -> None:
        """Initialize collaboration manager."""
        self.sessions: Dict[str, CollaborativeSession] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self._lock = threading.RLock()

        # Event handlers
        self._session_created_handlers: List[Callable] = []
        self._collaborator_joined_handlers: List[Callable] = []
        self._collaborator_left_handlers: List[Callable] = []
        self._permission_changed_handlers: List[Callable] = []

    def create_session(
        self,
        diagram_id: str,
        diagram_type: str,
        title: str,
        owner_id: str,
        owner_email: str,
        owner_name: str,
        settings: Optional[Dict[str, Any]] = None,
    ) -> CollaborativeSession:
        """
        Create a new collaborative session.

        Args:
            diagram_id: Unique diagram identifier
            diagram_type: Type of diagram
            title: Session title
            owner_id: Owner user ID
            owner_email: Owner email
            owner_name: Owner name
            settings: Session settings

        Returns:
            Created collaborative session
        """
        with self._lock:
            session_id = str(uuid.uuid4())
            now = datetime.now()

            # Create owner collaborator
            owner = Collaborator(
                user_id=owner_id,
                email=owner_email,
                name=owner_name,
                permission=Permission.OWNER,
                joined_at=now,
                last_active=now,
                is_online=True,
            )

            # Create session
            session = CollaborativeSession(
                session_id=session_id,
                diagram_id=diagram_id,
                diagram_type=diagram_type,
                title=title,
                owner_id=owner_id,
                created_at=now,
                updated_at=now,
                state=SessionState.ACTIVE,
                settings=settings or {},
            )

            session.add_collaborator(owner)

            # Store session
            self.sessions[session_id] = session

            # Update user sessions mapping
            if owner_id not in self.user_sessions:
                self.user_sessions[owner_id] = set()
            self.user_sessions[owner_id].add(session_id)

            # Notify handlers
            for handler in self._session_created_handlers:
                handler(session)

            return session

    def get_session(self, session_id: str) -> Optional[CollaborativeSession]:
        """Get session by ID."""
        with self._lock:
            return self.sessions.get(session_id)

    def add_collaborator(
        self,
        session_id: str,
        user_id: str,
        email: str,
        name: str,
        permission: Permission = Permission.VIEWER,
        invited_by: Optional[str] = None,
    ) -> bool:
        """
        Add collaborator to session.

        Args:
            session_id: Session ID
            user_id: User ID to add
            email: User email
            name: User name
            permission: User permission level
            invited_by: User ID who sent the invitation

        Returns:
            True if collaborator was added
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return False

            # Check if inviter has permission
            if invited_by and not session.can_edit(invited_by):
                return False

            # Create collaborator
            collaborator = Collaborator(
                user_id=user_id,
                email=email,
                name=name,
                permission=permission,
                joined_at=datetime.now(),
                last_active=datetime.now(),
                is_online=True,
            )

            session.add_collaborator(collaborator)

            # Update user sessions mapping
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)

            # Notify handlers
            for handler in self._collaborator_joined_handlers:
                handler(session, collaborator)

            return True

    def remove_collaborator(
        self,
        session_id: str,
        user_id: str,
        removed_by: Optional[str] = None,
    ) -> bool:
        """
        Remove collaborator from session.

        Args:
            session_id: Session ID
            user_id: User ID to remove
            removed_by: User ID who initiated removal

        Returns:
            True if collaborator was removed
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return False

            # Check permissions
            if removed_by and removed_by != user_id:
                if not session.can_edit(removed_by):
                    return False

            # Get collaborator before removal
            collaborator = session.get_collaborator(user_id)
            if not collaborator:
                return False

            # Remove collaborator
            success = session.remove_collaborator(user_id)
            if success:
                # Update user sessions mapping
                if user_id in self.user_sessions:
                    self.user_sessions[user_id].discard(session_id)
                    if not self.user_sessions[user_id]:
                        del self.user_sessions[user_id]

                # Notify handlers
                for handler in self._collaborator_left_handlers:
                    handler(session, collaborator)

            return success

    def update_collaborator_status(
        self,
        session_id: str,
        user_id: str,
        is_online: bool,
        cursor_position: Optional[Dict[str, Any]] = None,
        selection: Optional[List[str]] = None,
    ) -> bool:
        """
        Update collaborator status and presence.

        Args:
            session_id: Session ID
            user_id: User ID
            is_online: Online status
            cursor_position: Current cursor position
            selection: Selected elements

        Returns:
            True if status was updated
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return False

            collaborator = session.get_collaborator(user_id)
            if not collaborator:
                return False

            collaborator.set_online(is_online)

            if cursor_position is not None:
                collaborator.update_cursor(cursor_position)

            if selection is not None:
                collaborator.update_selection(selection)

            session.updated_at = datetime.now()
            return True

    def update_permission(
        self,
        session_id: str,
        user_id: str,
        new_permission: Permission,
        updated_by: str,
    ) -> bool:
        """
        Update collaborator permission.

        Args:
            session_id: Session ID
            user_id: User ID to update
            new_permission: New permission level
            updated_by: User ID making the change

        Returns:
            True if permission was updated
        """
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return False

            # Only owner can change permissions
            if updated_by != session.owner_id:
                return False

            success = session.update_collaborator_permission(user_id, new_permission)

            if success:
                collaborator = session.get_collaborator(user_id)
                # Notify handlers
                for handler in self._permission_changed_handlers:
                    handler(session, collaborator, new_permission)

            return success

    def get_user_sessions(self, user_id: str) -> List[CollaborativeSession]:
        """Get all sessions for a user."""
        with self._lock:
            session_ids = self.user_sessions.get(user_id, set())
            return [self.sessions[sid] for sid in session_ids if sid in self.sessions]

    def archive_session(self, session_id: str, archived_by: str) -> bool:
        """Archive a session."""
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return False

            # Only owner can archive
            if archived_by != session.owner_id:
                return False

            session.state = SessionState.ARCHIVED
            session.updated_at = datetime.now()

            # Set all collaborators offline
            for collaborator in session.collaborators.values():
                collaborator.set_online(False)

            return True

    def get_session_statistics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session statistics."""
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return None

            online_count = len(session.get_online_collaborators())
            total_count = len(session.collaborators)

            return {
                "session_id": session_id,
                "total_collaborators": total_count,
                "online_collaborators": online_count,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "state": session.state.value,
                "diagram_type": session.diagram_type,
            }

    # Event handler registration
    def on_session_created(
        self, handler: Callable[[CollaborativeSession], None]
    ) -> None:
        """Register session created handler."""
        self._session_created_handlers.append(handler)

    def on_collaborator_joined(
        self, handler: Callable[[CollaborativeSession, Collaborator], None]
    ) -> None:
        """Register collaborator joined handler."""
        self._collaborator_joined_handlers.append(handler)

    def on_collaborator_left(
        self, handler: Callable[[CollaborativeSession, Collaborator], None]
    ) -> None:
        """Register collaborator left handler."""
        self._collaborator_left_handlers.append(handler)

    def on_permission_changed(
        self, handler: Callable[[CollaborativeSession, Collaborator, Permission], None]
    ) -> None:
        """Register permission changed handler."""
        self._permission_changed_handlers.append(handler)
