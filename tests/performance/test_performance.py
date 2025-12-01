#!/usr/bin/env python3
"""
Test performance optimization functionality.
"""

import os
import sys
import tempfile
from unittest.mock import Mock, patch

import requests

from diagramaid.renderers.svg_renderer import SVGRenderer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


def test_caching_functionality() -> None:
    """Test caching functionality."""
    print("Testing caching functionality...")

    # Use temporary directory for cache
    with tempfile.TemporaryDirectory() as temp_dir:
        renderer = SVGRenderer(
            use_local=False, cache_enabled=True, cache_dir=temp_dir, cache_ttl=60
        )

        # Mock SVG response
        mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'

        with patch.object(requests.Session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_svg
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "image/svg+xml"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # First render - should miss cache
            result1 = renderer.render("flowchart TD\n    A --> B")
            assert result1 == mock_svg
            assert mock_get.call_count == 1

            # Second render - should hit cache
            result2 = renderer.render("flowchart TD\n    A --> B")
            assert result2 == mock_svg
            assert mock_get.call_count == 1  # No additional request

            # Check cache stats
            stats = renderer.get_cache_stats()
            print(f"Cache stats: {stats}")
            assert stats["cache_hits"] == 1
            assert stats["cache_misses"] == 1
            assert stats["hit_rate"] == 0.5
            print("✓ Caching functionality passed")


def test_cache_key_generation() -> None:
    """Test cache key generation."""
    print("\nTesting cache key generation...")

    renderer = SVGRenderer()

    # Same inputs should generate same key
    key1 = renderer._generate_cache_key(
        "flowchart TD\n    A --> B", "dark", {"width": 800}
    )
    key2 = renderer._generate_cache_key(
        "flowchart TD\n    A --> B", "dark", {"width": 800}
    )
    assert key1 == key2
    print("✓ Consistent cache key generation passed")

    # Different inputs should generate different keys
    key3 = renderer._generate_cache_key(
        "flowchart TD\n    A --> C", "dark", {"width": 800}
    )
    assert key1 != key3
    print("✓ Different cache key generation passed")

    # Different themes should generate different keys
    key4 = renderer._generate_cache_key(
        "flowchart TD\n    A --> B", "light", {"width": 800}
    )
    assert key1 != key4
    print("✓ Theme-based cache key generation passed")


def test_cache_management() -> None:
    """Test cache management operations."""
    print("\nTesting cache management...")

    with tempfile.TemporaryDirectory() as temp_dir:
        renderer = SVGRenderer(use_local=False, cache_enabled=True, cache_dir=temp_dir)

        # Mock and cache some content
        mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'

        with patch.object(requests.Session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_svg
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "image/svg+xml"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Create some cached content
            renderer.render("flowchart TD\n    A --> B")
            renderer.render("flowchart TD\n    C --> D")

            # Check cache stats
            stats = renderer.get_cache_stats()
            assert stats["total_files"] == 2
            print(f"Cache files created: {stats['total_files']}")

            # Clear cache
            removed_count = renderer.clear_cache()
            assert removed_count > 0
            print(f"Cache files removed: {removed_count}")

            # Verify cache is empty
            stats_after = renderer.get_cache_stats()
            assert stats_after["total_files"] == 0
            print("✓ Cache management passed")


def test_performance_metrics() -> None:
    """Test performance metrics tracking."""
    print("\nTesting performance metrics...")

    # Disable cache for this test
    renderer = SVGRenderer(use_local=False, cache_enabled=False)

    mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.text = mock_svg
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "image/svg+xml"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Make several requests
        for i in range(3):
            renderer.render(f"flowchart TD\n    A{i} --> B{i}")

        # Check metrics
        metrics = renderer.get_performance_metrics()
        print(f"Performance metrics: {metrics}")

        assert metrics["total_requests"] == 3
        assert metrics["cache_misses"] == 3
        assert metrics["cache_hits"] == 0
        assert len(renderer._metrics["render_times"]) == 3
        print("✓ Performance metrics tracking passed")


def test_large_diagram_optimization() -> None:
    """Test large diagram optimization analysis."""
    print("\nTesting large diagram optimization...")

    renderer = SVGRenderer()

    # Test small diagram
    small_diagram = "flowchart TD\n    A --> B"
    analysis = renderer.optimize_for_large_diagrams(small_diagram)
    print(f"Small diagram analysis: {analysis}")
    assert analysis["size_category"] == "small"
    assert analysis["estimated_render_time"] == "fast"
    print("✓ Small diagram analysis passed")

    # Test large diagram
    large_diagram = "flowchart TD\n" + "\n".join(
        [f"    A{i} --> A{i+1}" for i in range(60)]
    )
    analysis = renderer.optimize_for_large_diagrams(large_diagram)
    print(f"Large diagram analysis: {analysis}")
    assert analysis["size_category"] == "large"
    assert analysis["estimated_render_time"] == "slow"
    assert len(analysis["suggestions"]) > 0
    print("✓ Large diagram analysis passed")


def test_cache_preloading() -> None:
    """Test cache preloading functionality."""
    print("\nTesting cache preloading...")

    with tempfile.TemporaryDirectory() as temp_dir:
        renderer = SVGRenderer(use_local=False, cache_enabled=True, cache_dir=temp_dir)

        mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'

        with patch.object(requests.Session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_svg
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "image/svg+xml"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Preload configurations
            configs = [
                {"code": "flowchart TD\n    A --> B", "theme": "dark"},
                {"code": "flowchart TD\n    C --> D", "theme": "light"},
                {"code": "graph LR\n    E --> F"},
            ]

            results = renderer.preload_cache(configs)
            print(f"Preload results: {results}")

            assert results["successful"] == 3
            assert results["failed"] == 0

            # Verify cache was populated
            stats = renderer.get_cache_stats()
            assert stats["total_files"] == 3
            print("✓ Cache preloading passed")


def test_session_warmup() -> None:
    """Test session warm-up functionality."""
    print("\nTesting session warm-up...")

    renderer = SVGRenderer(use_local=False)

    mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'

    with patch.object(requests.Session, "get") as mock_get:
        mock_response = Mock()
        mock_response.text = mock_svg
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "image/svg+xml"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Test warm-up
        success = renderer.warm_up_session()
        assert success == True
        print("✓ Session warm-up passed")


if __name__ == "__main__":
    print("Testing performance optimizations...")

    test_caching_functionality()
    test_cache_key_generation()
    test_cache_management()
    test_performance_metrics()
    test_large_diagram_optimization()
    test_cache_preloading()
    test_session_warmup()

    print("\n🎉 All performance optimization tests passed!")
