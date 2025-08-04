#!/usr/bin/env python3
"""
Test script for the improved SVG renderer.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mermaid_render.renderers.svg_renderer import SVGRenderer
from unittest.mock import patch, Mock
import requests

def test_validation_methods():
    """Test the validation and sanitization methods."""
    print("Testing validation and sanitization methods...")
    
    renderer = SVGRenderer()
    
    # Test SVG validation
    valid_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>'
    invalid_svg = '<div>Not SVG</div>'
    empty_svg = ''
    
    print(f"Valid SVG validation: {renderer.validate_svg_content(valid_svg)}")
    print(f"Invalid SVG validation: {renderer.validate_svg_content(invalid_svg)}")
    print(f"Empty SVG validation: {renderer.validate_svg_content(empty_svg)}")
    
    # Test sanitization
    unsafe_svg = '<svg><script>alert("xss")</script><rect onclick="alert(1)"/></svg>'
    safe_svg = renderer.sanitize_svg_content(unsafe_svg)
    print(f"Original unsafe SVG: {unsafe_svg}")
    print(f"Sanitized SVG: {safe_svg}")
    
    # Test optimization
    unoptimized_svg = '<svg>  <!-- comment -->  <rect />  </svg>'
    optimized_svg = renderer.optimize_svg_content(unoptimized_svg)
    print(f"Original SVG: {unoptimized_svg}")
    print(f"Optimized SVG: {optimized_svg}")

def test_remote_rendering_mock():
    """Test remote rendering with mocked requests."""
    print("\nTesting remote rendering with mock...")
    
    # Mock SVG response
    mock_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect x="10" y="10" width="80" height="80" fill="blue"/>
    <text x="50" y="55" text-anchor="middle" fill="white">A</text>
</svg>'''
    
    with patch('mermaid_render.renderers.svg_renderer.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = mock_svg
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/svg+xml'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        renderer = SVGRenderer(use_local=False)
        try:
            result = renderer.render('flowchart TD\n    A --> B', validate=True, sanitize=True)
            print(f"Render successful: {len(result)} characters")
            print(f"Contains SVG tag: {'<svg' in result.lower()}")
            print(f"First 100 chars: {result[:100]}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

def test_error_handling():
    """Test error handling scenarios."""
    print("\nTesting error handling...")
    
    renderer = SVGRenderer(use_local=False)
    
    # Test empty input
    try:
        renderer.render('')
        print("ERROR: Should have failed with empty input")
    except Exception as e:
        print(f"Correctly caught empty input error: {e}")
    
    # Test network error
    with patch('mermaid_render.renderers.svg_renderer.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        try:
            renderer.render('flowchart TD\n    A --> B')
            print("ERROR: Should have failed with timeout")
        except Exception as e:
            print(f"Correctly caught timeout error: {e}")

def test_theme_validation():
    """Test theme validation."""
    print("\nTesting theme validation...")
    
    renderer = SVGRenderer()
    
    valid_themes = ['default', 'dark', 'forest', 'neutral', 'base']
    invalid_themes = ['invalid', 'nonexistent', '']
    
    for theme in valid_themes:
        result = renderer.validate_theme(theme)
        print(f"Theme '{theme}' validation: {result}")
    
    for theme in invalid_themes:
        result = renderer.validate_theme(theme)
        print(f"Theme '{theme}' validation: {result}")

if __name__ == "__main__":
    print("Testing improved SVG renderer...")
    
    test_validation_methods()
    test_remote_rendering_mock()
    test_error_handling()
    test_theme_validation()
    
    print("\nAll tests completed!")
