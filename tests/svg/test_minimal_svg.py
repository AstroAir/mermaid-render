#!/usr/bin/env python3
"""
Minimal test for SVG renderer functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

print("Starting minimal SVG test...")

try:
    print("1. Testing basic imports...")
    import requests
    print("   ✓ requests imported")
    
    from mermaid_render.exceptions import NetworkError, RenderingError
    print("   ✓ exceptions imported")
    
    print("2. Testing SVG renderer import...")
    # Let's try importing the module step by step
    import mermaid_render.renderers
    print("   ✓ renderers package imported")
    
    # Try importing the svg_renderer module directly
    import mermaid_render.renderers.svg_renderer as svg_module
    print("   ✓ svg_renderer module imported")
    
    # Try importing the class
    SVGRenderer = svg_module.SVGRenderer
    print("   ✓ SVGRenderer class imported")
    
    print("3. Testing renderer creation...")
    renderer = SVGRenderer(use_local=False)
    print("   ✓ Renderer created successfully")
    
    print("4. Testing basic properties...")
    print(f"   Server URL: {renderer.server_url}")
    print(f"   Timeout: {renderer.timeout}")
    print(f"   Use local: {renderer.use_local}")
    
    print("5. Testing session...")
    print(f"   Session type: {type(renderer._session)}")
    print(f"   Session headers: {dict(renderer._session.headers)}")
    
    print("6. Testing cleanup...")
    renderer.close()
    print("   ✓ Renderer closed successfully")
    
    print("\nAll tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
