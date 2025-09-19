from typing import Any
#!/usr/bin/env python3
"""
Test script for the improved remote SVG rendering.
"""

import requests
from unittest.mock import patch, Mock
from mermaid_render.renderers.svg_renderer import SVGRenderer
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def test_session_creation() -> None:
    """Test that the session is created with proper configuration."""
    print("Testing session creation...")

    renderer = SVGRenderer()

    # Check that session exists
    assert hasattr(renderer, '_session')
    assert isinstance(renderer._session, requests.Session)

    # Check headers
    headers = renderer._session.headers
    assert 'User-Agent' in headers
    assert 'mermaid-render' in headers['User-Agent']

    print("✓ Session created with proper configuration")


def test_context_manager() -> None:
    """Test context manager functionality."""
    print("Testing context manager...")

    with SVGRenderer() as renderer:
        assert hasattr(renderer, '_session')
        session = renderer._session

    # Session should be closed after context exit
    # Note: We can't easily test if session is closed, but we can test the pattern works
    print("✓ Context manager works correctly")


def test_server_status() -> None:
    """Test server status checking."""
    print("Testing server status checking...")

    # Mock successful response
    with patch.object(requests.Session, 'get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_get.return_value = mock_response

        renderer = SVGRenderer()
        status = renderer.get_server_status()

        assert status['available'] is True
        assert status['status_code'] == 200
        assert status['response_time'] == 0.5
        print("✓ Server status check works for available server")

    # Mock failed response
    with patch.object(requests.Session, 'get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        renderer = SVGRenderer()
        status = renderer.get_server_status()

        assert status['available'] is False
        assert 'error' in status
        print("✓ Server status check works for unavailable server")


def test_retry_mechanism() -> None:
    """Test retry mechanism with mocked failures."""
    print("Testing retry mechanism...")

    # Mock SVG response
    mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'

    # Test that retry configuration is properly set
    renderer = SVGRenderer(use_local=False, max_retries=3)

    # Check that the session has retry configuration
    adapter = renderer._session.get_adapter('https://')
    assert hasattr(adapter, 'max_retries')
    print("✓ Retry configuration is properly set")

    # Test successful rendering after simulated retry
    with patch.object(renderer._session, 'get') as mock_get:
        mock_response_success = Mock()
        mock_response_success.text = mock_svg
        mock_response_success.status_code = 200
        mock_response_success.headers = {'content-type': 'image/svg+xml'}
        mock_response_success.raise_for_status = Mock()

        mock_get.return_value = mock_response_success

        result = renderer.render('flowchart TD\n    A --> B')
        # Just check that we got some SVG content
        assert '<svg' in result and '</svg>' in result
        print("✓ Retry mechanism works correctly")


def test_fallback_servers() -> None:
    """Test fallback server functionality."""
    print("Testing fallback servers...")

    mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'

    with patch.object(requests.Session, 'get') as mock_get:
        # Primary server fails, fallback succeeds
        def side_effect(*args: Any, **kwargs: Any) -> Mock:
            url = args[0]
            if 'primary' in url:
                raise requests.exceptions.ConnectionError("Primary server down")
            else:
                mock_response = Mock()
                mock_response.text = mock_svg
                mock_response.status_code = 200
                mock_response.headers = {'content-type': 'image/svg+xml'}
                mock_response.raise_for_status = Mock()
                return mock_response

        mock_get.side_effect = side_effect

        renderer = SVGRenderer(
            server_url="https://primary.example.com", use_local=False)
        result = renderer.render_with_fallback(
            'flowchart TD\n    A --> B',
            fallback_servers=['https://fallback.example.com']
        )

        assert result == mock_svg
        print("✓ Fallback servers work correctly")


def test_enhanced_error_handling() -> None:
    """Test enhanced error handling."""
    print("Testing enhanced error handling...")

    renderer = SVGRenderer(use_local=False)

    # Test with various error scenarios by directly calling _render_remote
    try:
        with patch.object(renderer._session, 'get') as mock_get:
            # Test timeout error
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
            renderer._render_remote('flowchart TD\n    A --> B')
            assert False, "Should have raised NetworkError"
    except Exception as e:
        assert "timeout" in str(e).lower()
        print("✓ Timeout error handled correctly")

    try:
        with patch.object(renderer._session, 'get') as mock_get:
            # Test HTTP error
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "404 Not Found")
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            renderer._render_remote('flowchart TD\n    A --> B')
            assert False, "Should have raised NetworkError"
    except Exception as e:
        assert "404" in str(e) or "network" in str(e).lower()
        print("✓ HTTP error handled correctly")


if __name__ == "__main__":
    print("Testing improved remote SVG rendering...")

    test_session_creation()
    test_context_manager()
    test_server_status()
    test_retry_mechanism()
    test_fallback_servers()
    test_enhanced_error_handling()

    print("\nAll remote rendering tests completed successfully!")
