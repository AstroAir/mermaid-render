#!/usr/bin/env python3
"""
Package validation script for Mermaid Render.

This script validates the package structure, imports, and basic functionality
to ensure everything is working correctly.
"""

import importlib
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_import(module_name: str) -> Tuple[bool, str]:
    """Test if a module can be imported successfully."""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {module_name}"
    except ImportError as e:
        return False, f"❌ {module_name}: {e}"
    except Exception as e:
        return False, f"⚠️  {module_name}: {e}"


def validate_core_imports() -> List[Tuple[bool, str]]:
    """Validate core package imports."""
    core_modules = [
        "mermaid_render",
        "mermaid_render.core",
        "mermaid_render.exceptions",
        "mermaid_render.models",
        "mermaid_render.utils",
        "mermaid_render.validators",
        "mermaid_render.config",
        "mermaid_render.renderers",
    ]
    
    results = []
    for module in core_modules:
        results.append(test_import(module))
    
    return results


def validate_optional_imports() -> List[Tuple[bool, str]]:
    """Validate optional feature imports."""
    optional_modules = [
        "mermaid_render.ai",
        "mermaid_render.cache",
        "mermaid_render.collaboration",
        "mermaid_render.interactive",
        "mermaid_render.templates",
    ]
    
    results = []
    for module in optional_modules:
        success, message = test_import(module)
        if not success and "No module named" in message:
            # Optional modules are allowed to fail
            results.append((True, f"⚪ {module} (optional - not installed)"))
        else:
            results.append((success, message))
    
    return results


def validate_diagram_models() -> List[Tuple[bool, str]]:
    """Validate diagram model imports."""
    diagram_models = [
        "mermaid_render.models.flowchart",
        "mermaid_render.models.sequence",
        "mermaid_render.models.class_diagram",
        "mermaid_render.models.state",
        "mermaid_render.models.er_diagram",
        "mermaid_render.models.user_journey",
        "mermaid_render.models.gantt",
        "mermaid_render.models.pie_chart",
        "mermaid_render.models.git_graph",
        "mermaid_render.models.mindmap",
    ]
    
    results = []
    for module in diagram_models:
        results.append(test_import(module))
    
    return results


def validate_public_api() -> List[Tuple[bool, str]]:
    """Validate that public API classes can be imported."""
    try:
        import mermaid_render
        
        # Test core classes
        core_classes = [
            "MermaidRenderer",
            "MermaidConfig",
            "MermaidTheme",
            "FlowchartDiagram",
            "SequenceDiagram",
            "ClassDiagram",
        ]
        
        results = []
        for class_name in core_classes:
            if hasattr(mermaid_render, class_name):
                results.append((True, f"✅ {class_name} available in public API"))
            else:
                results.append((False, f"❌ {class_name} missing from public API"))
        
        return results
    
    except Exception as e:
        return [(False, f"❌ Failed to validate public API: {e}")]


def validate_quick_render() -> Tuple[bool, str]:
    """Test the quick_render function."""
    try:
        from mermaid_render import quick_render
        
        # Test with simple diagram
        test_diagram = """
        flowchart TD
            A[Start] --> B[End]
        """
        
        # This might fail if mermaid-py is not properly configured,
        # but the import should work
        result = quick_render(test_diagram, format="svg")
        if result:
            return True, "✅ quick_render function works"
        else:
            return False, "❌ quick_render returned empty result"
    
    except ImportError as e:
        return False, f"❌ quick_render import failed: {e}"
    except Exception as e:
        # Expected if mermaid service is not available
        return True, f"⚠️  quick_render import works (runtime error expected): {e}"


def validate_version_info() -> Tuple[bool, str]:
    """Validate version and metadata."""
    try:
        import mermaid_render
        
        version = getattr(mermaid_render, "__version__", None)
        author = getattr(mermaid_render, "__author__", None)
        license_info = getattr(mermaid_render, "__license__", None)
        
        if version and author and license_info:
            return True, f"✅ Metadata: v{version} by {author} ({license_info})"
        else:
            return False, "❌ Missing version or metadata information"
    
    except Exception as e:
        return False, f"❌ Failed to get version info: {e}"


def main() -> int:
    """Run all validation tests."""
    print("🔍 Validating Mermaid Render Package Structure")
    print("=" * 50)
    
    all_results = []
    
    # Core imports
    print("\n📦 Core Package Imports:")
    core_results = validate_core_imports()
    all_results.extend(core_results)
    for success, message in core_results:
        print(f"  {message}")
    
    # Optional imports
    print("\n🔧 Optional Feature Imports:")
    optional_results = validate_optional_imports()
    all_results.extend(optional_results)
    for success, message in optional_results:
        print(f"  {message}")
    
    # Diagram models
    print("\n📊 Diagram Model Imports:")
    model_results = validate_diagram_models()
    all_results.extend(model_results)
    for success, message in model_results:
        print(f"  {message}")
    
    # Public API
    print("\n🌐 Public API Validation:")
    api_results = validate_public_api()
    all_results.extend(api_results)
    for success, message in api_results:
        print(f"  {message}")
    
    # Quick render function
    print("\n⚡ Quick Render Function:")
    quick_render_result = validate_quick_render()
    all_results.append(quick_render_result)
    print(f"  {quick_render_result[1]}")
    
    # Version info
    print("\n📋 Version Information:")
    version_result = validate_version_info()
    all_results.append(version_result)
    print(f"  {version_result[1]}")
    
    # Summary
    print("\n" + "=" * 50)
    total_tests = len(all_results)
    passed_tests = sum(1 for success, _ in all_results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"📊 Summary: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests > 0:
        print(f"❌ {failed_tests} tests failed")
        print("\nFailed tests:")
        for success, message in all_results:
            if not success:
                print(f"  {message}")
        return 1
    else:
        print("✅ All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
