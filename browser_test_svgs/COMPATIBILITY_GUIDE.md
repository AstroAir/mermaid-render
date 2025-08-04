# Cross-Browser SVG Compatibility Testing Guide

## Overview
This guide helps you test the SVG output from mermaid-render across different browsers and viewing contexts.

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
