"""
Unit tests for collaboration module.
"""

import uuid
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from mermaid_render.collaboration import (
    CollaborationManager,
    CollaborativeSession,
    Collaborator,
    Permission,
    SessionState,
    VersionControl,
    DiffEngine,
    DiagramDiff,
    Change,
    ChangeType,
    MergeResolver,
    MergeStrategy,
    ConflictResolver,
    MergeConflict,
    ActivityLogger,
    ActivityType,
    CommentSystem,
    Comment,
)


class TestCollaborator:
    """Test Collaborator class."""

    def test_collaborator_creation(self):
        """Test basic collaborator creation."""
        now = datetime.now()
        collaborator = Collaborator(
            user_id="user123",
            email="user@example.com",
            name="Test User",
            permission=Permission.EDITOR,
            joined_at=now,
            last_active=now,
            is_online=True,
        )

        assert collaborator.user_id == "user123"
        assert collaborator.email == "user@example.com"
        assert collaborator.name == "Test User"
        assert collaborator.permission == Permission.EDITOR
        assert collaborator.is_online is True

    def test_collaborator_permissions(self):
        """Test collaborator permission levels."""
        permissions = [Permission.OWNER, Permission.EDITOR, Permission.VIEWER, Permission.COMMENTER]
        
        for perm in permissions:
            collaborator = Collaborator(
                user_id="user123",
                email="user@example.com",
                name="Test User",
                permission=perm,
                joined_at=datetime.now(),
                last_active=datetime.now(),
                is_online=True,
            )
            assert collaborator.permission == perm

    def test_collaborator_update_activity(self):
        """Test updating collaborator activity."""
        now = datetime.now()
        collaborator = Collaborator(
            user_id="user123",
            email="user@example.com",
            name="Test User",
            permission=Permission.EDITOR,
            joined_at=now,
            last_active=now,
            is_online=False,
        )

        collaborator.update_activity()
        assert collaborator.is_online is False  # update_activity doesn't change online status
        assert collaborator.last_active > now

        # Test set_online method
        collaborator.set_online(True)
        assert collaborator.is_online is True


class TestCollaborativeSession:
    """Test CollaborativeSession class."""

    def test_session_creation(self):
        """Test basic session creation."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = CollaborativeSession(
            session_id=session_id,
            diagram_id="diagram123",
            diagram_type="flowchart",
            title="Test Diagram",
            owner_id="owner123",
            created_at=now,
            updated_at=now,
            state=SessionState.ACTIVE,
            settings={},
        )

        assert session.session_id == session_id
        assert session.diagram_id == "diagram123"
        assert session.diagram_type == "flowchart"
        assert session.title == "Test Diagram"
        assert session.owner_id == "owner123"
        assert session.state == SessionState.ACTIVE
        assert len(session.collaborators) == 0

    def test_add_collaborator(self):
        """Test adding collaborator to session."""
        session = CollaborativeSession(
            session_id="session123",
            diagram_id="diagram123",
            diagram_type="flowchart",
            title="Test Diagram",
            owner_id="owner123",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            state=SessionState.ACTIVE,
            settings={},
        )

        collaborator = Collaborator(
            user_id="user123",
            email="user@example.com",
            name="Test User",
            permission=Permission.EDITOR,
            joined_at=datetime.now(),
            last_active=datetime.now(),
            is_online=True,
        )

        session.add_collaborator(collaborator)
        assert len(session.collaborators) == 1
        assert session.collaborators["user123"] == collaborator

    def test_remove_collaborator(self):
        """Test removing collaborator from session."""
        session = CollaborativeSession(
            session_id="session123",
            diagram_id="diagram123",
            diagram_type="flowchart",
            title="Test Diagram",
            owner_id="owner123",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            state=SessionState.ACTIVE,
            settings={},
        )

        collaborator = Collaborator(
            user_id="user123",
            email="user@example.com",
            name="Test User",
            permission=Permission.EDITOR,
            joined_at=datetime.now(),
            last_active=datetime.now(),
            is_online=True,
        )

        session.add_collaborator(collaborator)
        assert len(session.collaborators) == 1

        removed = session.remove_collaborator("user123")
        assert removed is True
        assert len(session.collaborators) == 0

        # Test removing non-existent collaborator
        removed = session.remove_collaborator("nonexistent")
        assert removed is False

    def test_permission_checks(self):
        """Test permission checking methods."""
        session = CollaborativeSession(
            session_id="session123",
            diagram_id="diagram123",
            diagram_type="flowchart",
            title="Test Diagram",
            owner_id="owner123",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            state=SessionState.ACTIVE,
            settings={},
        )

        # Add collaborators with different permissions
        editor = Collaborator(
            user_id="editor123",
            email="editor@example.com",
            name="Editor",
            permission=Permission.EDITOR,
            joined_at=datetime.now(),
            last_active=datetime.now(),
            is_online=True,
        )

        viewer = Collaborator(
            user_id="viewer123",
            email="viewer@example.com",
            name="Viewer",
            permission=Permission.VIEWER,
            joined_at=datetime.now(),
            last_active=datetime.now(),
            is_online=True,
        )

        session.add_collaborator(editor)
        session.add_collaborator(viewer)

        # Test edit permissions
        assert session.can_edit("editor123") is True
        assert session.can_edit("viewer123") is False
        assert session.can_edit("nonexistent") is False

        # Test comment permissions
        assert session.can_comment("editor123") is True
        assert session.can_comment("viewer123") is False


class TestCollaborationManager:
    """Test CollaborationManager class."""

    def test_manager_initialization(self):
        """Test collaboration manager initialization."""
        manager = CollaborationManager()

        assert isinstance(manager.sessions, dict)
        assert isinstance(manager.user_sessions, dict)
        assert len(manager.sessions) == 0

    def test_create_session(self):
        """Test creating a collaborative session."""
        manager = CollaborationManager()

        session = manager.create_session(
            diagram_id="diagram123",
            diagram_type="flowchart",
            owner_id="owner123",
            owner_email="owner@example.com",
            owner_name="Owner",
            title="Test Diagram",
        )

        assert session is not None
        assert session.diagram_id == "diagram123"
        assert session.owner_id == "owner123"
        assert session.title == "Test Diagram"
        assert session.session_id in manager.sessions
        assert len(session.collaborators) == 1  # Owner is added automatically

    def test_get_session(self):
        """Test retrieving a session."""
        manager = CollaborationManager()

        session = manager.create_session(
            diagram_id="diagram123",
            diagram_type="flowchart",
            title="Test Diagram",
            owner_id="owner123",
            owner_email="owner@example.com",
            owner_name="Owner",
        )

        retrieved = manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id

        # Test non-existent session
        assert manager.get_session("nonexistent") is None

    def test_add_collaborator(self):
        """Test adding collaborator to session."""
        manager = CollaborationManager()

        session = manager.create_session(
            diagram_id="diagram123",
            diagram_type="flowchart",
            title="Test Diagram",
            owner_id="owner123",
            owner_email="owner@example.com",
            owner_name="Owner",
        )

        result = manager.add_collaborator(
            session_id=session.session_id,
            user_id="user123",
            email="user@example.com",
            name="Test User",
            permission=Permission.EDITOR,
            invited_by="owner123",
        )

        assert result is True
        assert len(session.collaborators) == 2  # Owner + new collaborator
        assert "user123" in session.collaborators

    def test_remove_collaborator(self):
        """Test removing collaborator from session."""
        manager = CollaborationManager()

        session = manager.create_session(
            diagram_id="diagram123",
            diagram_type="flowchart",
            title="Test Diagram",
            owner_id="owner123",
            owner_email="owner@example.com",
            owner_name="Owner",
        )

        manager.add_collaborator(
            session_id=session.session_id,
            user_id="user123",
            email="user@example.com",
            name="Test User",
            permission=Permission.EDITOR,
            invited_by="owner123",
        )

        result = manager.remove_collaborator(session.session_id, "user123")
        assert result is True
        assert len(session.collaborators) == 1  # Only owner remains

    def test_get_user_sessions(self):
        """Test getting sessions for a user."""
        manager = CollaborationManager()

        # Create multiple sessions
        session1 = manager.create_session(
            diagram_id="diagram1",
            diagram_type="flowchart",
            title="Test Diagram 1",
            owner_id="user123",
            owner_email="user@example.com",
            owner_name="User",
        )

        session2 = manager.create_session(
            diagram_id="diagram2",
            diagram_type="sequence",
            title="Test Diagram 2",
            owner_id="user123",
            owner_email="user@example.com",
            owner_name="User",
        )

        user_sessions = manager.get_user_sessions("user123")
        assert len(user_sessions) == 2
        session_ids = [s.session_id for s in user_sessions]
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids


class TestDiffEngine:
    """Test DiffEngine class."""

    def test_diff_engine_creation(self):
        """Test diff engine initialization."""
        engine = DiffEngine()
        assert engine is not None

    def test_compute_diff_added_elements(self):
        """Test computing diff with added elements."""
        engine = DiffEngine()

        diagram1 = {"elements": {}}
        diagram2 = {
            "elements": {
                "node1": {"element_type": "node", "label": "New Node"}
            }
        }

        diff = engine.compute_diff(diagram1, diagram2)

        assert len(diff.changes) == 1
        assert diff.changes[0].change_type == ChangeType.ADD
        assert diff.changes[0].element_id == "node1"
        assert diff.summary["added"] == 1
        assert diff.summary["total"] == 1

    def test_compute_diff_deleted_elements(self):
        """Test computing diff with deleted elements."""
        engine = DiffEngine()

        diagram1 = {
            "elements": {
                "node1": {"element_type": "node", "label": "Old Node"}
            }
        }
        diagram2 = {"elements": {}}

        diff = engine.compute_diff(diagram1, diagram2)

        assert len(diff.changes) == 1
        assert diff.changes[0].change_type == ChangeType.DELETE
        assert diff.changes[0].element_id == "node1"
        assert diff.summary["deleted"] == 1

    def test_compute_diff_modified_elements(self):
        """Test computing diff with modified elements."""
        engine = DiffEngine()

        diagram1 = {
            "elements": {
                "node1": {"element_type": "node", "label": "Old Label"}
            }
        }
        diagram2 = {
            "elements": {
                "node1": {"element_type": "node", "label": "New Label"}
            }
        }

        diff = engine.compute_diff(diagram1, diagram2)

        assert len(diff.changes) == 1
        assert diff.changes[0].change_type == ChangeType.MODIFY
        assert diff.changes[0].element_id == "node1"
        assert diff.changes[0].old_value["label"] == "Old Label"
        assert diff.changes[0].new_value["label"] == "New Label"
        assert diff.summary["modified"] == 1

    def test_compute_diff_complex_changes(self):
        """Test computing diff with multiple types of changes."""
        engine = DiffEngine()

        diagram1 = {
            "elements": {
                "node1": {"element_type": "node", "label": "Old Label"},
                "node2": {"element_type": "node", "label": "To Delete"},
            }
        }
        diagram2 = {
            "elements": {
                "node1": {"element_type": "node", "label": "New Label"},
                "node3": {"element_type": "node", "label": "New Node"},
            }
        }

        diff = engine.compute_diff(diagram1, diagram2)

        assert len(diff.changes) == 3
        assert diff.summary["added"] == 1
        assert diff.summary["modified"] == 1
        assert diff.summary["deleted"] == 1
        assert diff.summary["total"] == 3


class TestMergeResolver:
    """Test MergeResolver class."""

    def test_merge_resolver_creation(self):
        """Test merge resolver initialization."""
        resolver = MergeResolver()
        assert resolver is not None
        assert isinstance(resolver.conflict_resolver, ConflictResolver)

    def test_merge_changes_no_conflicts(self):
        """Test merging changes without conflicts."""
        resolver = MergeResolver()

        base_diagram = {"elements": {}}
        
        source_changes = [
            Change(
                change_type=ChangeType.ADD,
                element_id="node1",
                element_type="node",
                new_value={"label": "Source Node"},
            )
        ]
        
        target_changes = [
            Change(
                change_type=ChangeType.ADD,
                element_id="node2",
                element_type="node",
                new_value={"label": "Target Node"},
            )
        ]

        merged = resolver.merge_changes(base_diagram, source_changes, target_changes)

        assert "elements" in merged
        assert len(merged["elements"]) == 2
        assert "node1" in merged["elements"]
        assert "node2" in merged["elements"]


class TestActivityLogger:
    """Test ActivityLogger class."""

    def test_activity_logger_creation(self):
        """Test activity logger initialization."""
        logger = ActivityLogger()
        assert len(logger.activities) == 0

    def test_log_activity(self):
        """Test logging an activity."""
        logger = ActivityLogger()

        logger.log_activity(
            activity_type=ActivityType.COLLABORATOR_JOINED,
            user_id="user123",
            user_name="Test User",
            session_id="session123",
            details={"user_name": "Test User"},
        )

        assert len(logger.activities) == 1
        activity_id = list(logger.activities.keys())[0]
        activity = logger.activities[activity_id]
        assert activity.activity_type == ActivityType.COLLABORATOR_JOINED
        assert activity.user_id == "user123"
        assert activity.details["user_name"] == "Test User"

    def test_get_activities_by_user(self):
        """Test getting activities for a specific user."""
        logger = ActivityLogger()

        logger.log_activity(ActivityType.COLLABORATOR_JOINED, "user1", "User 1", "session1", {})
        logger.log_activity(ActivityType.ELEMENT_MODIFIED, "user1", "User 1", "session1", {})
        logger.log_activity(ActivityType.COLLABORATOR_JOINED, "user2", "User 2", "session1", {})

        user1_activities = logger.get_activities_by_user("user1")
        assert len(user1_activities) == 2

        user2_activities = logger.get_activities_by_user("user2")
        assert len(user2_activities) == 1

    def test_get_activities_by_type(self):
        """Test getting activities by type."""
        logger = ActivityLogger()

        logger.log_activity(ActivityType.COLLABORATOR_JOINED, "user1", "User 1", "session1", {})
        logger.log_activity(ActivityType.COLLABORATOR_JOINED, "user2", "User 2", "session1", {})
        logger.log_activity(ActivityType.ELEMENT_MODIFIED, "user1", "User 1", "session1", {})

        join_activities = logger.get_activities_by_type(ActivityType.COLLABORATOR_JOINED)
        assert len(join_activities) == 2

        edit_activities = logger.get_activities_by_type(ActivityType.ELEMENT_MODIFIED)
        assert len(edit_activities) == 1


class TestCommentSystem:
    """Test CommentSystem class."""

    def test_comment_system_creation(self):
        """Test comment system initialization."""
        comment_system = CommentSystem()
        assert len(comment_system.comments) == 0

    def test_add_comment(self):
        """Test adding a comment."""
        comment_system = CommentSystem()

        comment = comment_system.add_comment(
            author_id="user123",
            author_name="Test User",
            content="This is a test comment",
            element_id="node1",
        )

        assert comment is not None
        assert comment.author_id == "user123"
        assert comment.content == "This is a test comment"
        assert comment.element_id == "node1"
        assert len(comment_system.comments) == 1

    def test_reply_to_comment(self):
        """Test replying to a comment."""
        comment_system = CommentSystem()

        original_comment = comment_system.add_comment(
            author_id="user123",
            author_name="User 123",
            content="Original comment",
            element_id="node1",
        )

        reply = comment_system.add_comment(
            author_id="user456",
            author_name="User 456",
            content="This is a reply",
            parent_comment_id=original_comment.comment_id,
        )

        assert reply is not None
        assert reply.parent_comment_id == original_comment.comment_id
        assert reply.content == "This is a reply"
        assert len(comment_system.comments) == 2

    def test_get_comments_for_element(self):
        """Test getting comments for a specific element."""
        comment_system = CommentSystem()

        comment_system.add_comment("user1", "User 1", "Comment on node1", "node1")
        comment_system.add_comment("user2", "User 2", "Another comment on node1", "node1")
        comment_system.add_comment("user3", "User 3", "Comment on node2", "node2")

        node1_comments = comment_system.get_comments_for_element("node1")
        assert len(node1_comments) == 2

        node2_comments = comment_system.get_comments_for_element("node2")
        assert len(node2_comments) == 1

    def test_resolve_comment(self):
        """Test resolving a comment."""
        comment_system = CommentSystem()

        comment = comment_system.add_comment(
            author_id="user123",
            author_name="User 123",
            content="This needs to be fixed",
            element_id="node1",
        )

        result = comment_system.resolve_comment(comment.comment_id)
        assert result is True
        assert comment.is_resolved is True
