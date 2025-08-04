#!/usr/bin/env python3
"""
Simple test for enhanced error handling functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mermaid_render.renderers.svg_renderer import SVGRenderer

def test_syntax_validation():
    """Test syntax validation functionality."""
    print("Testing syntax validation...")
    
    renderer = SVGRenderer()
    
    # Test valid syntax
    valid_code = "flowchart TD\n    A --> B"
    result = renderer.validate_mermaid_syntax(valid_code)
    print(f"Valid code result: {result}")
    assert result['is_valid'] == True
    print("✓ Valid syntax validation passed")
    
    # Test empty code
    result = renderer.validate_mermaid_syntax("")
    print(f"Empty code result: {result}")
    assert result['is_valid'] == False
    assert "Empty mermaid code" in result['errors']
    print("✓ Empty code validation passed")
    
    # Test code without diagram type
    no_type_code = "A --> B"
    result = renderer.validate_mermaid_syntax(no_type_code)
    print(f"No type code result: {result}")
    assert len(result['warnings']) > 0
    print("✓ Missing diagram type validation passed")

def test_error_suggestions():
    """Test error suggestion generation."""
    print("\nTesting error suggestions...")
    
    renderer = SVGRenderer()
    
    # Test timeout suggestions
    suggestions = renderer.get_error_suggestions("Request timeout after 30s")
    print(f"Timeout suggestions: {suggestions}")
    assert any("timeout" in s.lower() for s in suggestions)
    print("✓ Timeout suggestions generated")
    
    # Test network suggestions
    suggestions = renderer.get_error_suggestions("Network connection failed")
    print(f"Network suggestions: {suggestions}")
    assert any("connection" in s.lower() for s in suggestions)
    print("✓ Network suggestions generated")

def test_detailed_error_creation():
    """Test detailed error creation."""
    print("\nTesting detailed error creation...")
    
    renderer = SVGRenderer()
    
    # Test error with context
    base_error = ValueError("Test error")
    context = {"server_url": "https://example.com", "timeout": 30}
    
    detailed_error = renderer.create_detailed_error(base_error, context)
    error_str = str(detailed_error)
    print(f"Detailed error: {error_str}")
    
    assert "Test error" in error_str
    assert "server_url: https://example.com" in error_str
    assert "timeout: 30" in error_str
    print("✓ Detailed error creation passed")

def test_diagnostics():
    """Test rendering diagnostics."""
    print("\nTesting rendering diagnostics...")
    
    renderer = SVGRenderer()
    
    # Test diagnostics for simple code
    simple_code = "flowchart TD\n    A --> B"
    diagnosis = renderer.diagnose_rendering_issues(simple_code)
    print(f"Simple code diagnosis: {diagnosis}")
    
    assert 'syntax_check' in diagnosis
    assert 'server_status' in diagnosis
    assert 'recommendations' in diagnosis
    print("✓ Basic diagnostics passed")
    
    # Test diagnostics for complex code
    complex_code = "flowchart TD\n" + "\n".join([f"    A{i} --> A{i+1}" for i in range(60)])
    diagnosis = renderer.diagnose_rendering_issues(complex_code)
    print(f"Complex code diagnosis recommendations: {diagnosis['recommendations']}")
    
    assert any("nodes" in rec.lower() for rec in diagnosis['recommendations'])
    print("✓ Complex code diagnostics passed")

def test_svg_validation_and_sanitization():
    """Test SVG validation and sanitization."""
    print("\nTesting SVG validation and sanitization...")
    
    renderer = SVGRenderer()
    
    # Test valid SVG
    valid_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
    result = renderer.validate_svg_content(valid_svg)
    assert result['is_valid'] == True
    print("✓ Valid SVG validation passed")

    # Test invalid SVG
    invalid_svg = '<div>Not SVG</div>'
    result = renderer.validate_svg_content(invalid_svg)
    assert result['is_valid'] == False
    print("✓ Invalid SVG validation passed")
    
    # Test sanitization
    unsafe_svg = '<svg><script>alert("xss")</script><rect onclick="alert(1)"/></svg>'
    safe_svg = renderer.sanitize_svg_content(unsafe_svg)
    print(f"Sanitized SVG: {safe_svg}")
    assert '<script>' not in safe_svg
    assert 'onclick=' not in safe_svg
    print("✓ SVG sanitization passed")
    
    # Test optimization
    unoptimized = '<svg>  <!-- comment -->  <rect />  </svg>'
    optimized = renderer.optimize_svg_content(unoptimized)
    print(f"Optimized SVG: {optimized}")
    assert '<!--' not in optimized
    print("✓ SVG optimization passed")

if __name__ == "__main__":
    print("Testing enhanced error handling (simple)...")
    
    test_syntax_validation()
    test_error_suggestions()
    test_detailed_error_creation()
    test_diagnostics()
    test_svg_validation_and_sanitization()
    
    print("\n🎉 All enhanced error handling tests passed!")
