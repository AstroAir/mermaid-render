#!/usr/bin/env python3
"""
MCP Server Test Runner

This script provides an easy way to run the comprehensive MCP server tests
from the project root directory.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main test runner."""
    project_root = Path(__file__).parent
    mcp_test_dir = project_root / "tests" / "mcp"
    
    print("🧪 MCP Server Test Runner")
    print("=" * 50)
    
    # Check if MCP test directory exists
    if not mcp_test_dir.exists():
        print("❌ MCP test directory not found!")
        print(f"Expected: {mcp_test_dir}")
        return 1
    
    # Determine test mode
    test_mode = "full"
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            test_mode = "quick"
        elif sys.argv[1] == "mock":
            test_mode = "mock"
    
    print(f"Running {test_mode} test mode...")
    print(f"Test directory: {mcp_test_dir}")
    print()
    
    try:
        if test_mode == "mock":
            # Run mock demo
            print("🎭 Running mock demonstration...")
            result = subprocess.run([
                sys.executable, 
                str(mcp_test_dir / "test_mcp_mock_demo.py")
            ], cwd=project_root)
            
        else:
            # Run comprehensive tests
            print(f"🚀 Running {test_mode} MCP server tests...")
            result = subprocess.run([
                sys.executable, 
                str(mcp_test_dir / "run_mcp_tests.py"),
                test_mode
            ], cwd=project_root)
        
        return result.returncode
        
    except FileNotFoundError:
        print("❌ Python interpreter not found!")
        return 1
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    print("Usage:")
    print("  python run_mcp_tests.py        # Run full comprehensive test suite")
    print("  python run_mcp_tests.py quick  # Run quick test suite")
    print("  python run_mcp_tests.py mock   # Run mock demonstration")
    print()
    
    exit_code = main()
    sys.exit(exit_code)
