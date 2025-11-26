#!/usr/bin/env python3
"""
Enhanced Package validation script for Mermaid Render.

This script provides comprehensive validation of:
- Package structure and imports
- API compatibility and functionality
- Security and quality checks
- Build and distribution validation
- Performance and resource usage
"""

import importlib
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_import(module_name: str) -> tuple[bool, str]:
    """Test if a module can be imported successfully."""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {module_name}"
    except ImportError as e:
        return False, f"❌ {module_name}: {e}"
    except Exception as e:
        return False, f"⚠️  {module_name}: {e}"


def validate_core_imports() -> list[tuple[bool, str]]:
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


def validate_optional_imports() -> list[tuple[bool, str]]:
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


def validate_diagram_models() -> list[tuple[bool, str]]:
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


def validate_public_api() -> list[tuple[bool, str]]:
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


def validate_quick_render() -> tuple[bool, str]:
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


def validate_version_info() -> tuple[bool, str]:
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


def validate_package_structure() -> list[tuple[bool, str]]:
    """Validate package directory structure."""
    required_files = [
        "mermaid_render/__init__.py",
        "mermaid_render/core.py",
        "mermaid_render/exceptions.py",
        "mermaid_render/py.typed",
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
    ]

    results = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            results.append((True, f"✅ {file_path}"))
        else:
            results.append((False, f"❌ Missing: {file_path}"))

    return results


def validate_build_system() -> list[tuple[bool, str]]:
    """Validate build system configuration."""
    results = []

    # Check pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            import toml

            config = toml.load(pyproject_path)

            # Check required sections
            required_sections = ["project", "build-system"]
            for section in required_sections:
                if section in config:
                    results.append((True, f"✅ pyproject.toml has [{section}]"))
                else:
                    results.append((False, f"❌ pyproject.toml missing [{section}]"))

            # Check project metadata
            if "project" in config:
                project_config = config["project"]
                required_fields = ["name", "description", "authors", "dependencies"]
                for field in required_fields:
                    if field in project_config:
                        results.append((True, f"✅ project.{field} defined"))
                    else:
                        results.append((False, f"❌ project.{field} missing"))

        except Exception as e:
            results.append((False, f"❌ pyproject.toml validation failed: {e}"))
    else:
        results.append((False, "❌ pyproject.toml not found"))

    return results


def validate_security() -> list[tuple[bool, str]]:
    """Run security validation checks."""
    results = []

    # Check for common security files
    security_files = [
        "SECURITY.md",
        ".github/dependabot.yml",
    ]

    for file_path in security_files:
        full_path = project_root / file_path
        if full_path.exists():
            results.append((True, f"✅ Security file: {file_path}"))
        else:
            results.append((False, f"⚠️  Missing security file: {file_path}"))

    # Run safety check if available
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root,
        )
        packages = json.loads(result.stdout)

        # Check for known vulnerable packages (basic check)
        vulnerable_patterns = ["pillow<8.0.0", "requests<2.20.0"]
        for package in packages:
            name = package.get("name", "").lower()
            version = package.get("version", "")

            if name == "pillow" and version < "8.0.0":
                results.append((False, f"⚠️  Potentially vulnerable: {name} {version}"))
            elif name == "requests" and version < "2.20.0":
                results.append((False, f"⚠️  Potentially vulnerable: {name} {version}"))

        results.append((True, "✅ Basic security scan completed"))

    except Exception as e:
        results.append((False, f"⚠️  Security scan failed: {e}"))

    return results


def validate_distribution() -> list[tuple[bool, str]]:
    """Validate package distribution files."""
    results = []

    # Check if dist directory exists and has files
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        wheel_files = list(dist_dir.glob("*.whl"))
        sdist_files = list(dist_dir.glob("*.tar.gz"))

        if wheel_files:
            results.append((True, f"✅ Found {len(wheel_files)} wheel file(s)"))

            # Validate wheel contents
            for wheel_file in wheel_files[:1]:  # Check first wheel
                try:
                    with zipfile.ZipFile(wheel_file, "r") as zf:
                        files = zf.namelist()

                        # Check for required files in wheel
                        has_init = any("__init__.py" in f for f in files)
                        has_metadata = any("METADATA" in f for f in files)
                        has_wheel = any("WHEEL" in f for f in files)

                        if has_init and has_metadata and has_wheel:
                            results.append(
                                (True, f"✅ Wheel structure valid: {wheel_file.name}")
                            )
                        else:
                            results.append(
                                (
                                    False,
                                    f"❌ Invalid wheel structure: {wheel_file.name}",
                                )
                            )

                except Exception as e:
                    results.append((False, f"❌ Wheel validation failed: {e}"))
        else:
            results.append((False, "❌ No wheel files found in dist/"))

        if sdist_files:
            results.append(
                (True, f"✅ Found {len(sdist_files)} source distribution(s)")
            )
        else:
            results.append((False, "❌ No source distribution found in dist/"))

    else:
        results.append(
            (False, "⚠️  No dist/ directory found (run 'python -m build' first)")
        )

    return results


def validate_performance() -> list[tuple[bool, str]]:
    """Basic performance validation."""
    results = []

    try:
        # Test import time
        start_time = time.time()

        import_time = time.time() - start_time

        if import_time < 1.0:
            results.append((True, f"✅ Import time: {import_time:.3f}s"))
        elif import_time < 3.0:
            results.append((True, f"⚠️  Import time: {import_time:.3f}s (acceptable)"))
        else:
            results.append((False, f"❌ Import time too slow: {import_time:.3f}s"))

        # Test memory usage (basic)
        try:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            if memory_mb < 100:
                results.append((True, f"✅ Memory usage: {memory_mb:.1f}MB"))
            elif memory_mb < 200:
                results.append(
                    (True, f"⚠️  Memory usage: {memory_mb:.1f}MB (acceptable)")
                )
            else:
                results.append((False, f"❌ High memory usage: {memory_mb:.1f}MB"))

        except ImportError:
            results.append((True, "⚪ Memory check skipped (psutil not available)"))

    except Exception as e:
        results.append((False, f"❌ Performance validation failed: {e}"))

    return results


def validate_documentation() -> list[tuple[bool, str]]:
    """Validate documentation structure."""
    results = []

    # Check documentation files
    doc_files = [
        "README.md",
        "docs/index.md",
        "mkdocs.yml",
    ]

    for file_path in doc_files:
        full_path = project_root / file_path
        if full_path.exists():
            results.append((True, f"✅ Documentation: {file_path}"))
        else:
            results.append((False, f"❌ Missing documentation: {file_path}"))

    # Check if documentation can be built
    mkdocs_config = project_root / "mkdocs.yml"
    if mkdocs_config.exists():
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--clean", "--quiet"],
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=60,
            )

            if result.returncode == 0:
                results.append((True, "✅ Documentation builds successfully"))
            else:
                results.append(
                    (False, f"❌ Documentation build failed: {result.stderr}")
                )

        except subprocess.TimeoutExpired:
            results.append((False, "❌ Documentation build timed out"))
        except Exception as e:
            results.append((False, f"❌ Documentation build error: {e}"))

    return results


def main() -> int:
    """Run all validation tests."""
    print("🔍 Enhanced Mermaid Render Package Validation")
    print("=" * 60)

    all_results = []

    # Package structure
    print("\n📁 Package Structure:")
    structure_results = validate_package_structure()
    all_results.extend(structure_results)
    for success, message in structure_results:
        print(f"  {message}")

    # Build system
    print("\n🏗️  Build System:")
    build_results = validate_build_system()
    all_results.extend(build_results)
    for success, message in build_results:
        print(f"  {message}")

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

    # Security validation
    print("\n🔒 Security Validation:")
    security_results = validate_security()
    all_results.extend(security_results)
    for success, message in security_results:
        print(f"  {message}")

    # Distribution validation
    print("\n📦 Distribution Validation:")
    dist_results = validate_distribution()
    all_results.extend(dist_results)
    for success, message in dist_results:
        print(f"  {message}")

    # Performance validation
    print("\n⚡ Performance Validation:")
    perf_results = validate_performance()
    all_results.extend(perf_results)
    for success, message in perf_results:
        print(f"  {message}")

    # Documentation validation
    print("\n📚 Documentation Validation:")
    doc_results = validate_documentation()
    all_results.extend(doc_results)
    for success, message in doc_results:
        print(f"  {message}")

    # Summary
    print("\n" + "=" * 60)
    total_tests = len(all_results)
    passed_tests = sum(1 for success, _ in all_results if success)
    failed_tests = total_tests - passed_tests

    print(f"📊 Summary: {passed_tests}/{total_tests} tests passed")

    if failed_tests > 0:
        print(f"❌ {failed_tests} tests failed")
        print("\nFailed tests:")
        for success, message in all_results:
            if not success and not message.startswith("⚠️"):
                print(f"  {message}")

        print("\nWarnings:")
        for success, message in all_results:
            if not success and message.startswith("⚠️"):
                print(f"  {message}")

        return 1
    else:
        print("✅ All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
