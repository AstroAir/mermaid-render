#!/usr/bin/env python3
"""
Test enhanced SVG validation and sanitization functionality.
"""

from mermaid_render.renderers.svg_renderer import SVGRenderer
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def test_enhanced_svg_validation() -> None:
    """Test enhanced SVG validation."""
    print("Testing enhanced SVG validation...")

    renderer = SVGRenderer()

    # Test valid SVG
    valid_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect x="10" y="10" width="80" height="80" fill="blue"/>
</svg>'''

    result = renderer.validate_svg_content(valid_svg)
    print(f"Valid SVG result: {result}")
    assert result['is_valid'] == True
    assert len(result['errors']) == 0
    print("✓ Valid SVG validation passed")

    # Test SVG with security issues
    unsafe_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <script>alert('xss')</script>
    <rect onclick="alert('click')" width="100" height="100"/>
    <image href="javascript:alert('img')"/>
</svg>'''

    result = renderer.validate_svg_content(unsafe_svg, strict=True)
    print(f"Unsafe SVG result: {result}")
    assert result['is_valid'] == False  # Should fail in strict mode
    assert len(result['security_issues']) > 0
    print("✓ Unsafe SVG validation passed")

    # Test malformed SVG
    malformed_svg = '<svg><rect></svg>'  # Missing closing rect tag

    result = renderer.validate_svg_content(malformed_svg)
    print(f"Malformed SVG result: {result}")
    assert len(result['structure_issues']) > 0 or len(result['warnings']) > 0
    print("✓ Malformed SVG validation passed")


def test_enhanced_svg_sanitization() -> None:
    """Test enhanced SVG sanitization."""
    print("\nTesting enhanced SVG sanitization...")

    renderer = SVGRenderer()

    # Test script removal
    script_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <script type="text/javascript">alert('xss');</script>
    <rect width="100" height="100"/>
</svg>'''

    sanitized = renderer.sanitize_svg_content(script_svg)
    print(f"Script sanitized SVG: {sanitized}")
    assert '<script>' not in sanitized.lower()
    assert 'alert' not in sanitized
    print("✓ Script removal passed")

    # Test event handler removal
    event_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <rect onclick="alert('click')" onmouseover="alert('hover')" width="100" height="100"/>
</svg>'''

    sanitized = renderer.sanitize_svg_content(event_svg)
    print(f"Event sanitized SVG: {sanitized}")
    assert 'onclick=' not in sanitized
    assert 'onmouseover=' not in sanitized
    print("✓ Event handler removal passed")

    # Test dangerous URL removal
    url_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <image href="javascript:alert('img')"/>
    <a href="vbscript:alert('link')">Link</a>
</svg>'''

    sanitized = renderer.sanitize_svg_content(url_svg)
    print(f"URL sanitized SVG: {sanitized}")
    assert 'javascript:' not in sanitized
    assert 'vbscript:' not in sanitized
    print("✓ Dangerous URL removal passed")

    # Test strict mode
    foreign_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <foreignObject width="100" height="100">
        <div xmlns="http://www.w3.org/1999/xhtml">HTML content</div>
    </foreignObject>
</svg>'''

    sanitized_strict = renderer.sanitize_svg_content(foreign_svg, strict=True)
    sanitized_normal = renderer.sanitize_svg_content(foreign_svg, strict=False)

    print(f"Strict sanitized: {sanitized_strict}")
    print(f"Normal sanitized: {sanitized_normal}")

    assert 'foreignObject' not in sanitized_strict
    print("✓ Strict mode sanitization passed")


def test_svg_security_scanner() -> None:
    """Test SVG security scanner."""
    print("\nTesting SVG security scanner...")

    renderer = SVGRenderer()

    # Test high-risk SVG
    high_risk_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <script>alert('xss')</script>
    <iframe src="http://evil.com"></iframe>
</svg>'''

    scan_result = renderer.scan_svg_security(high_risk_svg)
    print(f"High-risk scan: {scan_result}")
    assert scan_result['risk_level'] == 'high'
    assert scan_result['safe_to_use'] == False
    assert len(scan_result['issues']) > 0
    print("✓ High-risk SVG detection passed")

    # Test medium-risk SVG
    medium_risk_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <rect onclick="doSomething()" width="100" height="100"/>
    <style>rect { fill: red; }</style>
</svg>'''

    scan_result = renderer.scan_svg_security(medium_risk_svg)
    print(f"Medium-risk scan: {scan_result}")
    assert scan_result['risk_level'] in ['medium', 'high']
    print("✓ Medium-risk SVG detection passed")

    # Test low-risk SVG
    low_risk_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="100" fill="blue"/>
    <text x="50" y="50">Safe text</text>
</svg>'''

    scan_result = renderer.scan_svg_security(low_risk_svg)
    print(f"Low-risk scan: {scan_result}")
    assert scan_result['risk_level'] == 'low'
    assert scan_result['safe_to_use'] == True
    print("✓ Low-risk SVG detection passed")


def test_svg_statistics() -> None:
    """Test SVG statistics generation."""
    print("\nTesting SVG statistics...")

    renderer = SVGRenderer()

    complex_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
    <g>
        <rect x="10" y="10" width="50" height="50"/>
        <circle cx="100" cy="100" r="30"/>
        <path d="M150,50 L180,80 L150,110 Z"/>
        <text x="50" y="150">Hello</text>
        <text x="100" y="150">World</text>
    </g>
</svg>'''

    stats = renderer._get_svg_statistics(complex_svg)
    print(f"SVG statistics: {stats}")

    assert stats['size'] > 0
    assert stats['elements'] > 0
    assert stats['text_elements'] == 2
    assert stats['paths'] == 1
    assert stats['shapes'] >= 2  # rect and circle
    assert stats['groups'] == 1
    print("✓ SVG statistics generation passed")


def test_svg_report() -> None:
    """Test comprehensive SVG report generation."""
    print("\nTesting SVG report generation...")

    renderer = SVGRenderer()

    test_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
    <rect onclick="alert('test')" width="100" height="100"/>
    <text>Sample text</text>
</svg>'''

    report = renderer.create_svg_report(test_svg)
    print(f"SVG report keys: {list(report.keys())}")

    assert 'validation' in report
    assert 'security' in report
    assert 'statistics' in report
    assert 'recommendations' in report

    # Should have security issues due to onclick
    assert len(report['security']['issues']) > 0
    assert len(report['recommendations']) > 0
    print("✓ SVG report generation passed")


def test_xml_structure_fixing() -> None:
    """Test XML structure fixing."""
    print("\nTesting XML structure fixing...")

    renderer = SVGRenderer()

    # Test self-closing tag fixing
    broken_svg = '<svg><rect x="10" y="10" width="50" height="50"><circle cx="30" cy="30" r="10"></svg>'

    fixed_svg = renderer._fix_xml_structure(broken_svg)
    print(f"Fixed SVG: {fixed_svg}")

    # Should have proper self-closing tags
    assert '<rect' in fixed_svg and '/>' in fixed_svg
    assert '<circle' in fixed_svg and '/>' in fixed_svg
    print("✓ XML structure fixing passed")


if __name__ == "__main__":
    print("Testing enhanced SVG validation and sanitization...")

    test_enhanced_svg_validation()
    test_enhanced_svg_sanitization()
    test_svg_security_scanner()
    test_svg_statistics()
    test_svg_report()
    test_xml_structure_fixing()

    print("\n🎉 All enhanced SVG validation and sanitization tests passed!")
