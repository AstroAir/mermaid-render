from typing import Any
#!/usr/bin/env python3
"""
Cross-browser compatibility test suite for SVG rendering.
Generates test SVGs and provides guidance for browser testing.
"""

import requests
from unittest.mock import patch, Mock
from diagramaid.renderers.svg_renderer import SVGRenderer
import sys
import os
import tempfile
import json
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def create_test_svgs() -> list[dict[str, str]]:
    """Create a comprehensive set of test SVGs for browser testing."""
    print("Creating test SVGs for cross-browser compatibility testing...")

    # Create test output directory
    test_dir = Path("browser_test_svgs")
    test_dir.mkdir(exist_ok=True)

    renderer = SVGRenderer(use_local=False)

    # Sample SVG content for different scenarios
    test_svgs = {
        'basic_flowchart': '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 300 200">
    <rect x="50" y="50" width="80" height="40" fill="#e1f5fe" stroke="#0277bd" stroke-width="2" rx="5"/>
    <text x="90" y="75" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">Start</text>
    <path d="M130 70 L170 70" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
    <rect x="170" y="50" width="80" height="40" fill="#f3e5f5" stroke="#7b1fa2" stroke-width="2" rx="5"/>
    <text x="210" y="75" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">End</text>
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>
        </marker>
    </defs>
</svg>''',

        'complex_shapes': '''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
    <circle cx="100" cy="100" r="40" fill="#ffeb3b" stroke="#f57f17" stroke-width="2"/>
    <ellipse cx="200" cy="100" rx="50" ry="30" fill="#4caf50" stroke="#2e7d32" stroke-width="2"/>
    <polygon points="300,60 340,100 300,140 260,100" fill="#ff5722" stroke="#d84315" stroke-width="2"/>
    <path d="M50 200 Q 100 150 150 200 T 250 200" stroke="#9c27b0" stroke-width="3" fill="none"/>
    <text x="200" y="250" text-anchor="middle" font-family="Arial" font-size="16" fill="#333">Complex Shapes Test</text>
</svg>''',

        'gradients_and_patterns': '''<svg xmlns="http://www.w3.org/2000/svg" width="350" height="250" viewBox="0 0 350 250">
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#ff9800;stop-opacity:1"/>
            <stop offset="100%" style="stop-color:#f44336;stop-opacity:1"/>
        </linearGradient>
        <radialGradient id="grad2" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#2196f3;stop-opacity:1"/>
            <stop offset="100%" style="stop-color:#3f51b5;stop-opacity:1"/>
        </radialGradient>
        <pattern id="pattern1" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
            <rect width="20" height="20" fill="#e8f5e8"/>
            <circle cx="10" cy="10" r="3" fill="#4caf50"/>
        </pattern>
    </defs>
    <rect x="50" y="50" width="100" height="60" fill="url(#grad1)"/>
    <circle cx="250" cy="80" r="40" fill="url(#grad2)"/>
    <rect x="100" y="150" width="150" height="50" fill="url(#pattern1)" stroke="#333" stroke-width="1"/>
    <text x="175" y="230" text-anchor="middle" font-family="Arial" font-size="14" fill="#333">Gradients &amp; Patterns</text>
</svg>''',

        'text_and_fonts': '''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
    <text x="200" y="50" text-anchor="middle" font-family="Arial" font-size="18" font-weight="bold" fill="#333">Font Test</text>
    <text x="50" y="100" font-family="Arial" font-size="14" fill="#666">Regular Arial Text</text>
    <text x="50" y="130" font-family="Times" font-size="14" fill="#666">Times Font Text</text>
    <text x="50" y="160" font-family="Courier" font-size="14" fill="#666">Monospace Text</text>
    <text x="50" y="190" font-family="Arial" font-size="12" font-style="italic" fill="#999">Italic Text</text>
    <text x="50" y="220" font-family="Arial" font-size="16" font-weight="bold" fill="#333">Bold Text</text>
    <text x="200" y="270" text-anchor="middle" font-family="Arial" font-size="10" fill="#999">Small Text (10px)</text>
</svg>''',

        'animations': '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 300 200">
    <circle cx="150" cy="100" r="20" fill="#2196f3">
        <animate attributeName="r" values="20;30;20" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="fill" values="#2196f3;#ff5722;#2196f3" dur="2s" repeatCount="indefinite"/>
    </circle>
    <rect x="100" y="150" width="100" height="20" fill="#4caf50">
        <animateTransform attributeName="transform" type="scale" values="1;1.2;1" dur="1.5s" repeatCount="indefinite"/>
    </rect>
    <text x="150" y="50" text-anchor="middle" font-family="Arial" font-size="14" fill="#333">Animation Test</text>
</svg>'''
    }

    # Generate test files
    test_results = []
    for name, svg_content in test_svgs.items():
        file_path = test_dir / f"{name}.svg"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        test_results.append({
            'name': name,
            'file': str(file_path),
            'description': get_test_description(name)
        })
        print(f"✓ Created {name}.svg")

    return test_results


def get_test_description(test_name: str) -> str:
    """Get description for each test case."""
    descriptions = {
        'basic_flowchart': 'Tests basic shapes, text rendering, and arrow markers',
        'complex_shapes': 'Tests circles, ellipses, polygons, and curved paths',
        'gradients_and_patterns': 'Tests linear/radial gradients and pattern fills',
        'text_and_fonts': 'Tests various font families, sizes, and styles',
        'animations': 'Tests SVG animations and transforms'
    }
    return descriptions.get(test_name, 'Test case')


def create_browser_test_html() -> Path:
    """Create an HTML file for browser testing."""
    print("\nCreating browser test HTML...")

    test_dir = Path("browser_test_svgs")
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid SVG Cross-Browser Compatibility Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .test-case {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #fafafa;
        }
        .test-case h3 {
            margin-top: 0;
            color: #333;
        }
        .svg-container {
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            background: white;
            border: 1px solid #eee;
            border-radius: 4px;
        }
        .browser-info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .checklist {
            background: #f1f8e9;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .checklist ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
            vertical-align: middle;
        }
        .pass { background-color: #4caf50; }
        .fail { background-color: #f44336; }
        .unknown { background-color: #ff9800; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Mermaid SVG Cross-Browser Compatibility Test</h1>
        
        <div class="browser-info">
            <h3>Browser Information</h3>
            <p><strong>User Agent:</strong> <span id="userAgent"></span></p>
            <p><strong>Browser:</strong> <span id="browserName"></span></p>
            <p><strong>Version:</strong> <span id="browserVersion"></span></p>
            <p><strong>Platform:</strong> <span id="platform"></span></p>
        </div>
        
        <div class="test-case">
            <h3>Basic Flowchart Test</h3>
            <p>Tests basic shapes, text rendering, and arrow markers</p>
            <div class="svg-container">
                <object data="basic_flowchart.svg" type="image/svg+xml" width="300" height="200">
                    Your browser does not support SVG
                </object>
            </div>
        </div>
        
        <div class="test-case">
            <h3>Complex Shapes Test</h3>
            <p>Tests circles, ellipses, polygons, and curved paths</p>
            <div class="svg-container">
                <object data="complex_shapes.svg" type="image/svg+xml" width="400" height="300">
                    Your browser does not support SVG
                </object>
            </div>
        </div>
        
        <div class="test-case">
            <h3>Gradients and Patterns Test</h3>
            <p>Tests linear/radial gradients and pattern fills</p>
            <div class="svg-container">
                <object data="gradients_and_patterns.svg" type="image/svg+xml" width="350" height="250">
                    Your browser does not support SVG
                </object>
            </div>
        </div>
        
        <div class="test-case">
            <h3>Text and Fonts Test</h3>
            <p>Tests various font families, sizes, and styles</p>
            <div class="svg-container">
                <object data="text_and_fonts.svg" type="image/svg+xml" width="400" height="300">
                    Your browser does not support SVG
                </object>
            </div>
        </div>
        
        <div class="test-case">
            <h3>Animations Test</h3>
            <p>Tests SVG animations and transforms</p>
            <div class="svg-container">
                <object data="animations.svg" type="image/svg+xml" width="300" height="200">
                    Your browser does not support SVG
                </object>
            </div>
        </div>
        
        <div class="checklist">
            <h3>Testing Checklist</h3>
            <p>Please verify the following in your browser:</p>
            <ul>
                <li>All SVG images load and display correctly</li>
                <li>Text is readable and properly positioned</li>
                <li>Colors and gradients render correctly</li>
                <li>Shapes have proper borders and fills</li>
                <li>Animations play smoothly (if supported)</li>
                <li>SVGs scale properly when zooming</li>
                <li>No JavaScript errors in console</li>
            </ul>
        </div>
    </div>
    
    <script>
        // Detect browser information
        const userAgent = navigator.userAgent;
        const platform = navigator.platform;
        
        document.getElementById('userAgent').textContent = userAgent;
        document.getElementById('platform').textContent = platform;
        
        // Simple browser detection
        let browserName = 'Unknown';
        let browserVersion = 'Unknown';
        
        if (userAgent.indexOf('Chrome') > -1) {
            browserName = 'Chrome';
            browserVersion = userAgent.match(/Chrome\\/([0-9.]+)/)?.[1] || 'Unknown';
        } else if (userAgent.indexOf('Firefox') > -1) {
            browserName = 'Firefox';
            browserVersion = userAgent.match(/Firefox\\/([0-9.]+)/)?.[1] || 'Unknown';
        } else if (userAgent.indexOf('Safari') > -1) {
            browserName = 'Safari';
            browserVersion = userAgent.match(/Version\\/([0-9.]+)/)?.[1] || 'Unknown';
        } else if (userAgent.indexOf('Edge') > -1) {
            browserName = 'Edge';
            browserVersion = userAgent.match(/Edge\\/([0-9.]+)/)?.[1] || 'Unknown';
        }
        
        document.getElementById('browserName').textContent = browserName;
        document.getElementById('browserVersion').textContent = browserVersion;
    </script>
</body>
</html>'''

    html_path = test_dir / "browser_test.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ Created browser test HTML: {html_path}")
    return html_path


def create_compatibility_report() -> Path:
    """Create a compatibility testing guide."""
    print("\nCreating compatibility testing guide...")

    guide_content = '''# Cross-Browser SVG Compatibility Testing Guide

## Overview
This guide helps you test the SVG output from diagramaid across different browsers and viewing contexts.

## Test Files Generated
- `basic_flowchart.svg` - Tests basic shapes, text, and arrows
- `complex_shapes.svg` - Tests various SVG shape elements
- `gradients_and_patterns.svg` - Tests advanced fill patterns
- `text_and_fonts.svg` - Tests text rendering capabilities
- `animations.svg` - Tests SVG animation support
- `browser_test.html` - Interactive browser testing page

## Browser Testing Matrix

### Desktop Browsers
| Browser | Version | SVG Support | Notes |
|---------|---------|-------------|-------|
| Chrome | 90+ | Excellent | Full SVG 1.1 support |
| Firefox | 88+ | Excellent | Full SVG 1.1 support |
| Safari | 14+ | Good | Some animation limitations |
| Edge | 90+ | Excellent | Full SVG 1.1 support |
| IE 11 | 11 | Limited | Basic SVG only, no animations |

### Mobile Browsers
| Browser | Platform | SVG Support | Notes |
|---------|----------|-------------|-------|
| Chrome Mobile | Android | Excellent | Same as desktop |
| Safari Mobile | iOS | Good | Performance may vary |
| Firefox Mobile | Android | Excellent | Same as desktop |
| Samsung Internet | Android | Good | Generally compatible |

## Testing Procedure

### 1. Visual Testing
1. Open `browser_test.html` in each target browser
2. Verify all SVG images display correctly
3. Check for proper text rendering and positioning
4. Ensure colors and gradients appear as expected
5. Test zooming and scaling behavior

### 2. Performance Testing
1. Monitor page load times
2. Check for smooth animations
3. Test with large/complex diagrams
4. Verify memory usage doesn't spike

### 3. Accessibility Testing
1. Test with screen readers
2. Verify keyboard navigation works
3. Check color contrast ratios
4. Test with high contrast mode

### 4. Integration Testing
1. Test SVGs embedded in different contexts:
   - Direct `<img>` tags
   - `<object>` elements
   - Inline SVG in HTML
   - CSS background images
   - PDF documents

## Common Issues and Solutions

### Text Rendering Issues
- **Problem**: Text appears blurry or poorly positioned
- **Solution**: Ensure proper font fallbacks and use web-safe fonts

### Animation Problems
- **Problem**: Animations don't play or are choppy
- **Solution**: Test with reduced motion preferences, provide static fallbacks

### Scaling Issues
- **Problem**: SVG doesn't scale properly
- **Solution**: Verify viewBox attributes and responsive CSS

### Color Inconsistencies
- **Problem**: Colors appear different across browsers
- **Solution**: Use standard color formats (hex, rgb) and test color profiles

## Automated Testing

### Browser Automation
```javascript
// Example Selenium test
const { Builder, By, until } = require('selenium-webdriver');

async function testSVGRendering() {
    let driver = await new Builder().forBrowser('chrome').build();
    try {
        await driver.get('file:///path/to/browser_test.html');
        
        // Wait for SVGs to load
        await driver.wait(until.elementLocated(By.css('object')), 5000);
        
        // Take screenshots for comparison
        await driver.takeScreenshot();
        
        // Check for console errors
        const logs = await driver.manage().logs().get('browser');
        console.log('Browser logs:', logs);
        
    } finally {
        await driver.quit();
    }
}
```

### Visual Regression Testing
- Use tools like Percy, Chromatic, or BackstopJS
- Compare screenshots across browser versions
- Set up CI/CD pipeline for automated testing

## Reporting Issues
When reporting compatibility issues, include:
1. Browser name and version
2. Operating system
3. Screenshot of the issue
4. Console error messages
5. Steps to reproduce

## Best Practices for SVG Compatibility
1. Use standard SVG 1.1 features
2. Provide fallbacks for advanced features
3. Test early and often across browsers
4. Keep SVG markup clean and valid
5. Optimize for performance on mobile devices
'''

    guide_path = Path("browser_test_svgs") / "COMPATIBILITY_GUIDE.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)

    print(f"✓ Created compatibility guide: {guide_path}")
    return guide_path


if __name__ == "__main__":
    print("Setting up cross-browser compatibility testing...")
    print("=" * 60)

    # Create test SVGs
    test_results = create_test_svgs()

    # Create browser test HTML
    html_path = create_browser_test_html()

    # Create compatibility guide
    guide_path = create_compatibility_report()

    print("\n" + "=" * 60)
    print("🎉 Cross-browser compatibility test suite created!")
    print(f"\nTest files created in: browser_test_svgs/")
    print(f"Open {html_path} in different browsers to test compatibility")
    print(f"See {guide_path} for detailed testing instructions")
    print("\nNext steps:")
    print("1. Open browser_test.html in Chrome, Firefox, Safari, and Edge")
    print("2. Verify all SVGs render correctly")
    print("3. Test on mobile devices")
    print("4. Report any issues found")
    print("5. Use the compatibility guide for systematic testing")
