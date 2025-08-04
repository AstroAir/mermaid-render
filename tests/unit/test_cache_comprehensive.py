"""
Comprehensive tests for cache system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import time
import json
from pathlib import Path

from mermaid_render.cache import (
    CacheManager,
    MemoryBackend,
    FileBackend,
    PerformanceMonitor,
    create_cache_manager,
)
from mermaid_render.exceptions import CacheError


class TestCacheManager:
    """Test cache manager functionality."""

    def test_cache_manager_creation(self):
        """Test creating a cache manager."""
        manager = create_cache_manager("memory")
        assert manager is not None

    def test_cache_manager_with_file_backend(self):
        """Test cache manager with file backend."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = create_cache_manager("file", cache_dir=temp_dir)
            assert manager is not None

    def test_cache_manager_basic_operations(self):
        """Test basic cache operations."""
        manager = create_cache_manager("memory")

        # Test that manager has expected methods
        assert hasattr(manager, 'get')
        assert hasattr(manager, 'put')
        assert hasattr(manager, 'clear')

        # Test basic put/get operations
        manager.put("test_key", "test_value")
        result = manager.get("test_key")
        assert result == "test_value"


class TestMemoryBackend:
    """Test memory backend implementation."""

    def test_memory_backend_creation(self):
        """Test memory backend creation."""
        backend = MemoryBackend()
        assert backend is not None

    def test_memory_backend_with_options(self):
        """Test memory backend with configuration options."""
        backend = MemoryBackend(max_entries=1000)
        assert backend is not None


class TestFileBackend:
    """Test file-based cache backend."""

    def test_file_backend_creation(self):
        """Test file backend creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(cache_dir=temp_dir)
            assert backend is not None

    def test_file_backend_with_options(self):
        """Test file backend with configuration options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backend = FileBackend(cache_dir=temp_dir, max_size_mb=50)
            assert backend is not None


class TestPerformanceMonitor:
    """Test performance monitoring functionality."""

    def test_performance_monitor_creation(self):
        """Test performance monitor creation."""
        monitor = PerformanceMonitor()
        assert monitor is not None

    def test_performance_monitor_with_cache_manager(self):
        """Test performance monitor integration with cache manager."""
        manager = create_cache_manager("memory")
        monitor = PerformanceMonitor()

        # Test that both objects exist and can be used together
        assert manager is not None
        assert monitor is not None
