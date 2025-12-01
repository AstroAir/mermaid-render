#!/usr/bin/env python3
"""
Comprehensive unit test runner for diagramaid project.

This script runs all unit tests with proper organization and reporting,
including the new comprehensive test suites for all modules.
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Union


def run_test_suite(test_path: str, verbose: bool = False, coverage: bool = False) -> Dict[str, Union[bool, int, str]]:
    """
    Run a specific test suite and return results.
    
    Args:
        test_path: Path to the test file or directory
        verbose: Whether to run in verbose mode
        coverage: Whether to collect coverage data
        
    Returns:
        Dictionary with test results
    """
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if coverage:
        cmd.extend(["--cov=diagramaid", "--cov-report=term-missing"])
    
    cmd.append(test_path)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "test_path": test_path
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Test suite {test_path} timed out after 5 minutes",
            "test_path": test_path
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Error running test suite {test_path}: {str(e)}",
            "test_path": test_path
        }


def get_test_suites() -> List[str]:
    """Get list of all test suites to run."""
    test_suites = [
        # Core functionality tests
        "tests/unit/test_core.py",
        "tests/unit/test_convenience.py",
        "tests/unit/test_exceptions.py",
        "tests/unit/test_cli.py",
        "tests/unit/test_error_handling.py",

        # MCP tests
        "tests/unit/mcp/test_mcp_server.py",

        # Renderer tests
        "tests/unit/renderers/test_base.py",
        "tests/unit/renderers/test_renderers.py",
        "tests/unit/renderers/test_new_renderers.py",
        "tests/unit/renderers/test_plugin_architecture.py",

        # Cache module tests
        "tests/unit/cache/test_backends.py",
        "tests/unit/cache/test_cache_manager.py",
        "tests/unit/cache/test_strategies.py",
        "tests/unit/cache/test_performance.py",
        "tests/unit/cache/test_utils.py",
        "tests/unit/cache/test_cache.py",

        # Model tests
        "tests/unit/models/test_flowchart.py",
        "tests/unit/models/test_sequence.py",
        "tests/unit/models/test_class_diagram.py",
        "tests/unit/models/test_er_diagram.py",
        "tests/unit/models/test_diagram_types.py",

        # Interactive module tests
        "tests/unit/interactive/test_builder.py",
        "tests/unit/interactive/test_export.py",
        "tests/unit/interactive/test_security.py",
        "tests/unit/interactive/test_templates.py",
        "tests/unit/interactive/test_ui_components.py",
        "tests/unit/interactive/test_utils.py",
        # Interactive builder tests
        "tests/unit/interactive/builder/test_diagram_builder.py",
        "tests/unit/interactive/builder/test_element_manager.py",
        "tests/unit/interactive/builder/test_connection_manager.py",
        "tests/unit/interactive/builder/test_event_manager.py",
        "tests/unit/interactive/builder/test_serialization.py",
        # Interactive builder codegen tests
        "tests/unit/interactive/builder/codegen/test_base.py",
        "tests/unit/interactive/builder/codegen/test_flowchart.py",
        "tests/unit/interactive/builder/codegen/test_sequence.py",
        "tests/unit/interactive/builder/codegen/test_class_diagram.py",
        # Interactive builder parsers tests
        "tests/unit/interactive/builder/parsers/test_base.py",
        "tests/unit/interactive/builder/parsers/test_flowchart.py",
        "tests/unit/interactive/builder/parsers/test_sequence.py",
        "tests/unit/interactive/builder/parsers/test_class_diagram.py",
        "tests/unit/interactive/builder/parsers/test_er_diagram.py",
        "tests/unit/interactive/builder/parsers/test_state_diagram.py",
        # Interactive models tests
        "tests/unit/interactive/models/test_elements.py",
        "tests/unit/interactive/models/test_enums.py",
        "tests/unit/interactive/models/test_geometry.py",
        # Interactive routes tests
        "tests/unit/interactive/routes/test_elements.py",
        "tests/unit/interactive/routes/test_preview.py",
        "tests/unit/interactive/routes/test_sessions.py",
        # Interactive server tests
        "tests/unit/interactive/server/test_interactive_server.py",
        "tests/unit/interactive/server/test_app_factory.py",
        "tests/unit/interactive/server/test_middleware.py",
        "tests/unit/interactive/server/test_page_routes.py",
        "tests/unit/interactive/server/test_router_registration.py",
        "tests/unit/interactive/server/test_websocket_endpoint.py",
        # Interactive websocket tests
        "tests/unit/interactive/websocket/test_websocket_handler.py",
        "tests/unit/interactive/websocket/test_session_manager.py",
        "tests/unit/interactive/websocket/test_message_dispatcher.py",
        "tests/unit/interactive/websocket/test_broadcast_service.py",

        # Validator tests
        "tests/unit/validators/test_validator.py",
        "tests/unit/validators/test_validators.py",

        # Configuration tests
        "tests/unit/config/test_config_manager.py",
        "tests/unit/config/test_theme_manager.py",

        # Template tests
        "tests/unit/templates/test_templates.py",

        # AI module tests
        "tests/unit/ai/test_ai_comprehensive.py",
        "tests/unit/ai/test_ai_improved.py",
        "tests/unit/ai/test_analysis.py",
        "tests/unit/ai/test_compatibility.py",
        "tests/unit/ai/test_diagram_generator.py",
        "tests/unit/ai/test_nl_processor.py",
        "tests/unit/ai/test_providers.py",
        "tests/unit/ai/test_suggestions.py",
        "tests/unit/ai/test_utils.py",

        # Utility tests
        "tests/unit/utils/test_utils.py",
        "tests/unit/utils/test_export.py",
        "tests/unit/utils/test_helpers.py",
        "tests/unit/utils/test_validation.py",

        # Plugin tests
        "tests/unit/test_plugin_renderer.py",
    ]
    
    # Filter to only existing test files
    existing_suites = []
    for suite in test_suites:
        if Path(suite).exists():
            existing_suites.append(suite)
        else:
            print(f"Warning: Test suite {suite} not found, skipping...")
    
    return existing_suites


def print_summary(results: List[Dict[str, Union[bool, int, str]]]) -> None:
    """Print test results summary."""
    total_suites = len(results)
    passed_suites = sum(1 for r in results if r["success"])
    failed_suites = total_suites - passed_suites
    
    print("\n" + "="*80)
    print("COMPREHENSIVE UNIT TEST SUMMARY")
    print("="*80)
    print(f"Total test suites: {total_suites}")
    print(f"Passed: {passed_suites}")
    print(f"Failed: {failed_suites}")
    print(f"Success rate: {(passed_suites/total_suites)*100:.1f}%")
    
    if failed_suites > 0:
        print("\nFAILED TEST SUITES:")
        print("-" * 40)
        for result in results:
            if not result["success"]:
                print(f"❌ {result['test_path']}")
                if result["stderr"]:
                    print(f"   Error: {str(result['stderr'])[:200]}...")
    
    print("\nPASSED TEST SUITES:")
    print("-" * 40)
    for result in results:
        if result["success"]:
            print(f"✅ {result['test_path']}")
    
    print("="*80)


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive unit tests for diagramaid"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Collect coverage data"
    )
    parser.add_argument(
        "-f", "--fail-fast",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "-s", "--suite",
        type=str,
        help="Run specific test suite (path relative to project root)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available test suites"
    )
    
    args = parser.parse_args()
    
    # Get test suites
    test_suites = get_test_suites()
    
    if args.list:
        print("Available test suites:")
        for suite in test_suites:
            status = "✅" if Path(suite).exists() else "❌"
            print(f"  {status} {suite}")
        return 0
    
    # Run specific suite if requested
    if args.suite:
        if args.suite not in test_suites:
            print(f"Error: Test suite '{args.suite}' not found")
            return 1
        test_suites = [args.suite]
    
    print(f"Running {len(test_suites)} test suites...")
    print("="*80)
    
    results = []
    
    for i, suite in enumerate(test_suites, 1):
        print(f"[{i}/{len(test_suites)}] Running {suite}...")
        
        result = run_test_suite(
            suite,
            verbose=args.verbose,
            coverage=args.coverage and i == len(test_suites)  # Only on last run
        )
        
        results.append(result)
        
        if result["success"]:
            print(f"✅ {suite} - PASSED")
        else:
            print(f"❌ {suite} - FAILED")
            if args.verbose and result["stderr"]:
                print(f"   Error: {result['stderr']}")
        
        if args.fail_fast and not result["success"]:
            print("\nStopping due to --fail-fast flag")
            break
        
        print("-" * 80)
    
    # Print summary
    print_summary(results)
    
    # Return appropriate exit code
    failed_count = sum(1 for r in results if not r["success"])
    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
