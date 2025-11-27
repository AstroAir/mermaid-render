"""
Unit tests for interactive.websocket.session_manager module.

Tests the SessionManager and DiagramSession classes.
"""

import pytest
from unittest.mock import Mock, patch

from mermaid_render.interactive.websocket.session_manager import (
    DiagramSession,
    SessionManager,
)


@pytest.mark.unit
class TestDiagramSession:
    """Unit tests for DiagramSession class."""

    def test_initialization(self) -> None:
        """Test DiagramSession initialization."""
        session = DiagramSession(session_id="test_session")
        assert session.session_id == "test_session"

    def test_session_has_id(self) -> None:
        """Test that session has ID."""
        session = DiagramSession(session_id="sess123")
        assert session.session_id == "sess123"

    def test_session_stores_diagram_data(self) -> None:
        """Test that session stores diagram data."""
        session = DiagramSession(session_id="test")
        session.diagram_data = {"elements": [], "connections": []}
        assert session.diagram_data is not None


@pytest.mark.unit
class TestSessionManager:
    """Unit tests for SessionManager class."""

    def test_initialization(self) -> None:
        """Test SessionManager initialization."""
        manager = SessionManager()
        assert manager is not None

    def test_create_session(self) -> None:
        """Test creating a new session."""
        manager = SessionManager()
        session = manager.create_session()
        assert session is not None
        assert session.session_id is not None

    def test_get_session(self) -> None:
        """Test getting session by ID."""
        manager = SessionManager()
        session = manager.create_session()
        retrieved = manager.get_session(session.session_id)
        assert retrieved == session

    def test_get_nonexistent_session(self) -> None:
        """Test getting non-existent session."""
        manager = SessionManager()
        result = manager.get_session("nonexistent")
        assert result is None

    def test_delete_session(self) -> None:
        """Test deleting session."""
        manager = SessionManager()
        session = manager.create_session()
        manager.delete_session(session.session_id)
        assert manager.get_session(session.session_id) is None

    def test_list_sessions(self) -> None:
        """Test listing all sessions."""
        manager = SessionManager()
        manager.create_session()
        manager.create_session()
        sessions = manager.list_sessions()
        assert len(sessions) >= 2

    def test_session_count(self) -> None:
        """Test session count."""
        manager = SessionManager()
        initial_count = manager.session_count()
        manager.create_session()
        assert manager.session_count() == initial_count + 1
