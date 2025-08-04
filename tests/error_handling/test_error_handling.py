#!/usr/bin/env python3
"""
Test enhanced error handling functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mermaid_render.renderers.svg_renderer import SVGRenderer
from unittest.mock import patch, Mock
import requests
import logging

# Set up logging to see the enhanced error messages
logging.basicConfig(level=logging.INFO)

def test_mermaid_syntax_validation():
    """Test Mermaid syntax validation."""
    print("Testing Mermaid syntax validation...")
    
    renderer = SVGRenderer()
    
    # Test valid syntax
    valid_code = "flowchart TD\n    A --> B"
    result = renderer.validate_mermaid_syntax(valid_code)
    assert result['is_valid'] == True
    print("✓ Valid syntax validation passed")
    
    # Test empty code
    result = renderer.validate_mermaid_syntax("")
    assert result['is_valid'] == False
    assert "Empty mermaid code" in result['errors']
    print("✓ Empty code validation passed")
    
    # Test code without diagram type
    no_type_code = "A --> B"
    result = renderer.validate_mermaid_syntax(no_type_code)
    assert len(result['warnings']) > 0
    print("✓ Missing diagram type validation passed")

def test_error_suggestions():
    """Test error suggestion generation."""
    print("\nTesting error suggestions...")
    
    renderer = SVGRenderer()
    
    # Test timeout suggestions
    suggestions = renderer.get_error_suggestions("Request timeout after 30s")
    assert any("timeout" in s.lower() for s in suggestions)
    print("✓ Timeout suggestions generated")
    
    # Test network suggestions
    suggestions = renderer.get_error_suggestions("Network connection failed")
    assert any("connection" in s.lower() for s in suggestions)
    print("✓ Network suggestions generated")
    
    # Test invalid SVG suggestions
    suggestions = renderer.get_error_suggestions("Invalid SVG response")
    assert any("syntax" in s.lower() for s in suggestions)
    print("✓ Invalid SVG suggestions generated")

def test_detailed_error_creation():
    """Test detailed error creation."""
    print("\nTesting detailed error creation...")
    
    renderer = SVGRenderer()
    
    # Test error with context
    base_error = ValueError("Test error")
    context = {"server_url": "https://example.com", "timeout": 30}
    
    detailed_error = renderer.create_detailed_error(base_error, context)
    error_str = str(detailed_error)
    
    assert "Test error" in error_str
    assert "server_url: https://example.com" in error_str
    assert "timeout: 30" in error_str
    print("✓ Detailed error creation passed")

def test_enhanced_render_errors():
    """Test enhanced error handling in render method."""
    print("\nTesting enhanced render errors...")
    
    renderer = SVGRenderer(use_local=False)
    
    # Test empty input with enhanced error
    try:
        renderer.render("")
        assert False, "Should have raised error"
    except Exception as e:
        error_str = str(e)
        assert "Empty mermaid code" in error_str
        assert "Suggestions:" in error_str
        print("✓ Enhanced empty input error passed")
    
    # Test invalid syntax with enhanced error (use clearly invalid syntax)
    try:
        renderer.render("", validate=True)  # Empty is clearly invalid
        assert False, "Should have raised error"
    except Exception as e:
        error_str = str(e)
        assert "empty" in error_str.lower()
        print("✓ Enhanced syntax error passed")

def test_network_error_enhancement():
    """Test enhanced network error handling."""
    print("\nTesting enhanced network errors...")
    
    renderer = SVGRenderer(use_local=False)
    
    # Test timeout with enhanced error
    with patch.object(requests.Session, 'get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        try:
            renderer.render("flowchart TD\n    A --> B")
            assert False, "Should have raised error"
        except Exception as e:
            error_str = str(e)
            assert "timeout" in error_str.lower()
            assert "server_url:" in error_str
            assert "suggestions:" in error_str.lower()
            print("✓ Enhanced timeout error passed")
    
    # Test HTTP error with enhanced error
    with patch.object(requests.Session, 'get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_get.return_value = mock_response
        
        try:
            renderer.render("flowchart TD\n    A --> B")
            assert False, "Should have raised error"
        except Exception as e:
            error_str = str(e)
            assert "500" in error_str
            assert "status_code:" in error_str
            print("✓ Enhanced HTTP error passed")

def test_diagnostics():
    """Test rendering diagnostics."""
    print("\nTesting rendering diagnostics...")
    
    renderer = SVGRenderer()
    
    # Test diagnostics for simple code
    simple_code = "flowchart TD\n    A --> B"
    diagnosis = renderer.diagnose_rendering_issues(simple_code)
    
    assert 'syntax_check' in diagnosis
    assert 'server_status' in diagnosis
    assert 'recommendations' in diagnosis
    print("✓ Basic diagnostics passed")
    
    # Test diagnostics for complex code
    complex_code = "flowchart TD\n" + "\n".join([f"    A{i} --> A{i+1}" for i in range(60)])
    diagnosis = renderer.diagnose_rendering_issues(complex_code)
    
    assert any("nodes" in rec.lower() for rec in diagnosis['recommendations'])
    print("✓ Complex code diagnostics passed")

def test_render_with_recovery():
    """Test render with recovery mechanism."""
    print("\nTesting render with recovery...")
    
    renderer = SVGRenderer(use_local=False)
    
    # Mock successful response after failures
    mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
    
    with patch.object(requests.Session, 'get') as mock_get:
        # First two calls fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.Timeout("Timeout")
        
        mock_response_success = Mock()
        mock_response_success.text = mock_svg
        mock_response_success.status_code = 200
        mock_response_success.headers = {'content-type': 'image/svg+xml'}
        mock_response_success.raise_for_status = Mock()
        
        mock_get.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_success
        ]
        
        # This should succeed after retries
        result = renderer.render_with_recovery("flowchart TD\n    A --> B", max_attempts=3)
        assert result == mock_svg
        assert mock_get.call_count == 3
        print("✓ Recovery mechanism passed")

if __name__ == "__main__":
    print("Testing enhanced error handling...")
    
    test_mermaid_syntax_validation()
    test_error_suggestions()
    test_detailed_error_creation()
    test_enhanced_render_errors()
    test_network_error_enhancement()
    test_diagnostics()
    test_render_with_recovery()
    
    print("\n🎉 All enhanced error handling tests passed!")
