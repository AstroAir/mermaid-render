#!/usr/bin/env python3
"""
Comprehensive test runner for the mermaid-render project.

This script runs all tests with detailed reporting and coverage analysis.
"""

import subprocess
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def main() -> bool:
    """Run comprehensive tests."""
    print("Mermaid Render - Comprehensive Test Suite")
    print("=" * 60)

    # Change to project directory
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")

    # Test categories to run
    test_categories = [
        {
            "name": "Core Functionality Tests",
            "path": "tests/unit/test_core.py",
            "description": "Core rendering and configuration tests"
        },
        {
            "name": "Diagram Types Tests",
            "path": "tests/unit/test_diagram_types_comprehensive.py",
            "description": "Comprehensive diagram type tests"
        },
        {
            "name": "Cache System Tests",
            "path": "tests/unit/test_cache_comprehensive.py",
            "description": "Cache system functionality tests"
        },
        {
            "name": "Renderer Tests",
            "path": "tests/unit/test_renderers.py",
            "description": "SVG, PNG, and PDF renderer tests"
        },
        {
            "name": "Validation Tests",
            "path": "tests/unit/test_validators.py",
            "description": "Diagram validation tests"
        },
        {
            "name": "Error Handling Tests",
            "path": "tests/error_handling/",
            "description": "Error handling and recovery tests"
        },
        {
            "name": "Integration Tests",
            "path": "tests/integration/",
            "description": "Integration and end-to-end tests"
        },
        {
            "name": "Performance Tests",
            "path": "tests/performance/",
            "description": "Performance and load tests"
        }
    ]

    # Run individual test categories
    results: Dict[str, Optional[bool]] = {}
    for test_category in test_categories:
        test_path = project_root / test_category["path"]
        if test_path.exists():
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_path),
                "-v",
                "--tb=short"
            ]
            success = run_command(
                cmd, f"{test_category['name']} - {test_category['description']}")
            results[test_category["name"]] = success
        else:
            print(f"Skipping {test_category['name']} - path does not exist: {test_path}")
            results[test_category["name"]] = None

    # Run coverage analysis
    print(f"\n{'='*60}")
    print("Running Coverage Analysis")
    print(f"{'='*60}")

    coverage_cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=mermaid_render",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--tb=no",
        "-q",
        "--ignore=tests/unit/test_ai_features_comprehensive.py",
        "--ignore=tests/unit/test_templates_comprehensive.py"
    ]

    coverage_success = run_command(coverage_cmd, "Coverage Analysis")

    # Run specific test patterns
    print(f"\n{'='*60}")
    print("Running Specific Test Patterns")
    print(f"{'='*60}")

    test_patterns = [
        {
            "pattern": "test_*_comprehensive.py",
            "description": "All comprehensive test files"
        },
        {
            "pattern": "test_*_edge_cases*",
            "description": "Edge case tests"
        },
        {
            "pattern": "test_*_error*",
            "description": "Error handling tests"
        }
    ]

    for test_pattern in test_patterns:
        cmd = [
            sys.executable, "-m", "pytest",
            "-k", test_pattern["pattern"],
            "-v",
            "--tb=short"
        ]
        pattern_success = run_command(cmd, f"Pattern: {test_pattern['description']}")
        results[f"Pattern: {test_pattern['pattern']}"] = pattern_success

    # Generate summary report
    print(f"\n{'='*60}")
    print("TEST EXECUTION SUMMARY")
    print(f"{'='*60}")

    total_tests = len([r for r in results.values() if r is not None])
    passed_tests = len([r for r in results.values() if r is True])
    failed_tests = len([r for r in results.values() if r is False])
    skipped_tests = len([r for r in results.values() if r is None])

    print(f"Total test categories: {len(results)}")
    print(f"Executed: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Skipped: {skipped_tests}")

    print(f"\nDetailed Results:")
    for category, result in results.items():
        # category: str, result: Optional[bool]
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⏭️  SKIPPED"
        print(f"  {status} {category}")

    print(f"\nCoverage Report: {'✅ Generated' if coverage_success else '❌ Failed'}")

    if coverage_success:
        print(f"HTML Coverage Report: {project_root}/htmlcov/index.html")

    # Test quality metrics
    print(f"\n{'='*60}")
    print("TEST QUALITY METRICS")
    print(f"{'='*60}")

    # Count test files
    test_files = list(Path(project_root / "tests").rglob("test_*.py"))
    print(f"Total test files: {len(test_files)}")

    # Count comprehensive test files
    comprehensive_files = list(Path(project_root / "tests").rglob("*comprehensive*.py"))
    print(f"Comprehensive test files: {len(comprehensive_files)}")

    # Test categories covered
    test_dirs = [d for d in (project_root / "tests").iterdir() if d.is_dir()]
    print(f"Test categories: {len(test_dirs)}")
    for test_dir in sorted(test_dirs):
        test_count = len(list(test_dir.rglob("test_*.py")))
        print(f"  - {test_dir.name}: {test_count} test files")

    # Final recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")

    if failed_tests > 0:
        print("❌ Some tests failed. Please review and fix failing tests.")

    if passed_tests / total_tests >= 0.8:
        print("✅ Good test coverage! Most test categories are passing.")
    else:
        print("⚠️  Consider improving test reliability.")

    print("📊 Review the HTML coverage report for detailed coverage analysis.")
    print("🔧 Consider adding more tests for areas with low coverage.")
    print("🚀 Run performance tests regularly to catch regressions.")

    return failed_tests == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
