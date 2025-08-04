#!/usr/bin/env python3
"""
Test SVG rendering functionality with mocked responses.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mermaid_render.renderers.svg_renderer import SVGRenderer
from unittest.mock import patch, Mock
import requests

def test_svg_rendering_with_mock():
    """Test SVG rendering with mocked response."""
    print("Testing SVG rendering with mock...")
    
    # Sample SVG response
    mock_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" viewBox="0 0 200 100">
    <rect x="10" y="10" width="80" height="30" fill="#f9f9f9" stroke="#333" stroke-width="1"/>
    <text x="50" y="30" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">A</text>
    <path d="M90 25 L110 25" stroke="#333" stroke-width="1" marker-end="url(#arrowhead)"/>
    <rect x="110" y="10" width="80" height="30" fill="#f9f9f9" stroke="#333" stroke-width="1"/>
    <text x="150" y="30" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">B</text>
</svg>'''
    
    with patch.object(requests.Session, 'get') as mock_get:
        mock_response = Mock()
        mock_response.text = mock_svg
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/svg+xml'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        renderer = SVGRenderer(use_local=False)
        
        # Test basic rendering
        result = renderer.render('flowchart TD\n    A --> B')
        print(f"✓ Basic rendering successful: {len(result)} characters")
        assert '<svg' in result
        assert 'xmlns' in result
        
        # Test rendering with theme
        result_themed = renderer.render('flowchart TD\n    A --> B', theme='dark')
        print(f"✓ Themed rendering successful: {len(result_themed)} characters")
        
        # Test rendering with config
        config = {'width': 800, 'height': 600}
        result_config = renderer.render('flowchart TD\n    A --> B', config=config)
        print(f"✓ Config rendering successful: {len(result_config)} characters")
        
        # Test validation and sanitization
        result_validated = renderer.render('flowchart TD\n    A --> B', validate=True, sanitize=True)
        print(f"✓ Validated rendering successful: {len(result_validated)} characters")
        
        renderer.close()

def test_svg_validation():
    """Test SVG validation functionality."""
    print("\nTesting SVG validation...")
    
    renderer = SVGRenderer()
    
    # Test valid SVG
    valid_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
    assert renderer.validate_svg_content(valid_svg) == True
    print("✓ Valid SVG validation passed")
    
    # Test invalid SVG
    invalid_svg = '<div>Not SVG</div>'
    assert renderer.validate_svg_content(invalid_svg) == False
    print("✓ Invalid SVG validation passed")
    
    # Test empty SVG
    assert renderer.validate_svg_content('') == False
    print("✓ Empty SVG validation passed")

def test_svg_sanitization():
    """Test SVG sanitization functionality."""
    print("\nTesting SVG sanitization...")
    
    renderer = SVGRenderer()
    
    # Test removing scripts
    unsafe_svg = '<svg><script>alert("xss")</script><rect/></svg>'
    safe_svg = renderer.sanitize_svg_content(unsafe_svg)
    assert '<script>' not in safe_svg
    print("✓ Script removal passed")
    
    # Test removing event handlers
    unsafe_svg2 = '<svg><rect onclick="alert(1)"/></svg>'
    safe_svg2 = renderer.sanitize_svg_content(unsafe_svg2)
    assert 'onclick=' not in safe_svg2
    print("✓ Event handler removal passed")

def test_svg_optimization():
    """Test SVG optimization functionality."""
    print("\nTesting SVG optimization...")
    
    renderer = SVGRenderer()
    
    # Test comment removal and whitespace optimization
    unoptimized = '<svg>  <!-- comment -->  <rect />  </svg>'
    optimized = renderer.optimize_svg_content(unoptimized)
    assert '<!--' not in optimized
    assert optimized.count(' ') < unoptimized.count(' ')
    print("✓ SVG optimization passed")

def test_error_handling():
    """Test error handling scenarios."""
    print("\nTesting error handling...")
    
    renderer = SVGRenderer(use_local=False)
    
    # Test empty input
    try:
        renderer.render('')
        assert False, "Should have raised error"
    except Exception as e:
        assert "empty" in str(e).lower()
        print("✓ Empty input error handling passed")
    
    # Test network error simulation
    with patch.object(requests.Session, 'get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        try:
            renderer.render('flowchart TD\n    A --> B')
            assert False, "Should have raised error"
        except Exception as e:
            assert "timeout" in str(e).lower()
            print("✓ Network timeout error handling passed")

def test_file_output():
    """Test file output functionality."""
    print("\nTesting file output...")
    
    mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
    
    with patch.object(requests.Session, 'get') as mock_get:
        mock_response = Mock()
        mock_response.text = mock_svg
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/svg+xml'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        renderer = SVGRenderer(use_local=False)
        
        # Test file output
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            output_path = f.name
        
        try:
            renderer.render_to_file('flowchart TD\n    A --> B', output_path)
            
            # Verify file was created and contains SVG
            with open(output_path, 'r') as f:
                content = f.read()
                assert '<svg' in content
                print("✓ File output passed")
        finally:
            import os
            if os.path.exists(output_path):
                os.unlink(output_path)

if __name__ == "__main__":
    print("Testing SVG rendering functionality...")
    
    test_svg_rendering_with_mock()
    test_svg_validation()
    test_svg_sanitization()
    test_svg_optimization()
    test_error_handling()
    test_file_output()
    
    print("\n🎉 All SVG rendering tests passed!")
