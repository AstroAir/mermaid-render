"""
Unit tests for interactive.websocket.session_manager module.

Tests the SessionManager and DiagramSession classes.
"""

import pytest
from unittest.mock import Mock

from mermaid_render.interactive.builder import DiagramBuilder
from mermaid_render.interactive.websocket.session_manager import (
    DiagramSession,
    SessionManager,
)


@pytest.mark.unit
class TestDiagramSession:
    """Unit tests for DiagramSession class."""

    def test_initialization(self) -> None:
        """Test DiagramSession initialization."""
        builder = DiagramBuilder()
        session = DiagramSession(session_id="test_session", builder=builder)
        assert session.session_id == "test_session"
        assert session.builder is builder

    def test_session_has_id(self) -> None:
        """Test that session has ID."""
        builder = DiagramBuilder()
        session = DiagramSession(session_id="sess123", builder=builder)
        assert session.session_id == "sess123"

    def test_add_client(self) -> None:
        """Test adding client to session."""
        builder = DiagramBuilder()
        session = DiagramSession(session_id="test", builder=builder)
        mock_ws = Mock()
        session.add_client(mock_ws)
        assert mock_ws in session.connected_clients

    def test_remove_client(self) -> None:
        """Test removing client from session."""
        builder = DiagramBuilder()
        session = DiagramSession(session_id="test", builder=builder)
        mock_ws = Mock()
        session.add_client(mock_ws)
        session.remove_client(mock_ws)
        assert mock_ws not in session.connected_clients

    def test_get_client_count(self) -> None:
        """Test getting client count."""
        builder = DiagramBuilder()
        session = DiagramSession(session_id="test", builder=builder)
        assert session.get_client_count() == 0
        session.add_client(Mock())
        assert session.get_client_count() == 1

    def test_is_empty(self) -> None:
        """Test checking if session is empty."""
        builder = DiagramBuilder()
        session = DiagramSession(session_id="test", builder=builder)
        assert session.is_empty() is True
        session.add_client(Mock())
        assert session.is_empty() is False


@pytest.mark.unit
class TestSessionManager:
    """Unit tests for SessionManager class."""

    def test_initialization(self) -> None:
        """Test SessionManager initialization."""
        manager = SessionManager()
        assert manager is not None
        assert manager.max_sessions == 100

    def test_create_session(self) -> None:
        """Test creating a new session."""
        manager = SessionManager()
        builder = DiagramBuilder()
        session = manager.create_session("sess1", builder)
        assert session is not None
        assert session.session_id == "sess1"

    def test_get_session(self) -> None:
        """Test getting session by ID."""
        manager = SessionManager()
        builder = DiagramBuilder()
        session = manager.create_session("sess1", builder)
        retrieved = manager.get_session("sess1")
        assert retrieved == session

    def test_get_nonexistent_session(self) -> None:
        """Test getting non-existent session."""
        manager = SessionManager()
        result = manager.get_session("nonexistent")
        assert result is None

    def test_remove_session(self) -> None:
        """Test removing session."""
        manager = SessionManager()
        builder = DiagramBuilder()
        manager.create_session("sess1", builder)
        result = manager.remove_session("sess1")
        assert result is True
        assert manager.get_session("sess1") is None

    def test_has_session(self) -> None:
        """Test checking if session exists."""
        manager = SessionManager()
        builder = DiagramBuilder()
        manager.create_session("sess1", builder)
        assert manager.has_session("sess1") is True
        assert manager.has_session("nonexistent") is False

    def test_get_session_count(self) -> None:
        """Test session count."""
        manager = SessionManager()
        builder = DiagramBuilder()
        initial_count = manager.get_session_count()
        manager.create_session("sess1", builder)
        assert manager.get_session_count() == initial_count + 1
