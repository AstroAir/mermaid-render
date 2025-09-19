#!/usr/bin/env python3
"""
Test SVG rendering fixes and improvements.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mermaid_render.renderers.svg_renderer import SVGRenderer


def test_malformed_self_closing_tags() -> None:
    """Test fixing malformed self-closing tags."""
    print("Testing malformed self-closing tag fixes...")
    
    renderer = SVGRenderer()
    
    # Test SVG with malformed self-closing tags
    malformed_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="50" height="50"//>
    <circle cx="30" cy="30" r="10"//>
    <path d="M10,10 L50,50"//>
</svg>'''
    
    fixed_svg = renderer._fix_xml_structure(malformed_svg)
    print(f"Fixed SVG: {fixed_svg}")
    
    # Should not contain '//>
    assert '//>' not in fixed_svg
    # Should contain proper self-closing tags
    assert 'rect x="10" y="10" width="50" height="50"/>' in fixed_svg
    assert 'circle cx="30" cy="30" r="10"/>' in fixed_svg
    assert 'path d="M10,10 L50,50"/>' in fixed_svg
    print("✓ Malformed self-closing tag fixes passed")


def test_namespace_fixes() -> None:
    """Test SVG namespace fixes."""
    print("\nTesting SVG namespace fixes...")
    
    renderer = SVGRenderer()
    
    # Test SVG without namespace
    svg_without_ns = '<svg width="100" height="100"><rect x="10" y="10" width="50" height="50"/></svg>'
    
    fixed_svg = renderer._fix_xml_structure(svg_without_ns)
    print(f"Fixed SVG: {fixed_svg}")
    
    # Should contain proper namespace
    assert 'xmlns="http://www.w3.org/2000/svg"' in fixed_svg
    print("✓ Namespace fixes passed")


def test_compatibility_fixes() -> None:
    """Test SVG compatibility fixes."""
    print("\nTesting SVG compatibility fixes...")
    
    renderer = SVGRenderer()
    
    # Test SVG with compatibility issues
    problematic_svg = '''<svg viewbox="0 0 100 100" width="100" height="100">
    <rect x="10" y="10" width=50 height=30 fill="blue"/>
</svg>'''
    
    fixed_svg = renderer._fix_compatibility_issues(problematic_svg)
    print(f"Fixed SVG: {fixed_svg}")
    
    # Should fix viewBox casing
    assert 'viewBox="0 0 100 100"' in fixed_svg
    # Should add quotes to unquoted attributes
    assert 'width="50"' in fixed_svg
    assert 'height="30"' in fixed_svg
    print("✓ Compatibility fixes passed")


def test_improved_validation() -> None:
    """Test improved SVG validation."""
    print("\nTesting improved SVG validation...")
    
    renderer = SVGRenderer()
    
    # Test SVG with style elements (should not trigger warnings)
    svg_with_style = '''<svg xmlns="http://www.w3.org/2000/svg">
    <style>
        .my-class { fill: red; }
    </style>
    <rect class="my-class" x="10" y="10" width="50" height="50"/>
</svg>'''
    
    result = renderer.validate_svg_content(svg_with_style)
    print(f"Validation result: {result}")
    
    # Should be valid
    assert result['is_valid'] == True
    # Should not have warnings about style elements
    style_warnings = [w for w in result['warnings'] if 'style' in w.lower()]
    assert len(style_warnings) == 0
    print("✓ Improved validation passed")


def test_enhanced_sanitization() -> None:
    """Test enhanced SVG sanitization."""
    print("\nTesting enhanced SVG sanitization...")
    
    renderer = SVGRenderer()
    
    # Test SVG with various event handlers
    unsafe_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <rect onclick="alert('click')" onmouseover="alert('hover')" x="10" y="10" width="50" height="50"/>
    <circle onload=dangerous() cx="30" cy="30" r="10"/>
</svg>'''
    
    sanitized_svg = renderer.sanitize_svg_content(unsafe_svg)
    print(f"Sanitized SVG: {sanitized_svg}")
    
    # Should remove all event handlers
    assert 'onclick=' not in sanitized_svg
    assert 'onmouseover=' not in sanitized_svg
    assert 'onload=' not in sanitized_svg
    assert 'dangerous()' not in sanitized_svg
    print("✓ Enhanced sanitization passed")


def test_complete_svg_processing() -> None:
    """Test complete SVG processing pipeline."""
    print("\nTesting complete SVG processing pipeline...")
    
    renderer = SVGRenderer()
    
    # Test SVG with multiple issues
    problematic_svg = '''<svg viewbox="0 0 100 100" width=100 height=100>
    <rect onclick="alert('test')" x="10" y="10" width="50" height="50"//>
    <circle cx="30" cy="30" r="10"//>
</svg>'''
    
    # Process through sanitization
    processed_svg = renderer.sanitize_svg_content(problematic_svg, strict=False)
    print(f"Processed SVG: {processed_svg}")
    
    # Validate the result
    result = renderer.validate_svg_content(processed_svg)
    print(f"Final validation: {result}")
    
    # Should be valid after processing
    assert result['is_valid'] == True
    # Should have proper namespace
    assert 'xmlns="http://www.w3.org/2000/svg"' in processed_svg
    # Should not have malformed tags
    assert '//>' not in processed_svg
    # Should not have event handlers
    assert 'onclick=' not in processed_svg
    # Should have proper viewBox casing
    assert 'viewBox=' in processed_svg
    print("✓ Complete SVG processing passed")


if __name__ == "__main__":
    print("Testing SVG rendering fixes and improvements...")
    
    test_malformed_self_closing_tags()
    test_namespace_fixes()
    test_compatibility_fixes()
    test_improved_validation()
    test_enhanced_sanitization()
    test_complete_svg_processing()
    
    print("\n🎉 All SVG fix tests passed!")
