#!/usr/bin/env python3
"""
Simple test runner for MCP server integration tests.

This script provides an easy way to run the comprehensive MCP server tests
without requiring pytest installation.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tests.mcp.test_mcp_server_integration import run_quick_test, run_full_test_suite
except ImportError as e:
    print(f"❌ Failed to import test modules: {e}")
    print("Make sure FastMCP and diagramaid are properly installed.")
    sys.exit(1)


async def main():
    """Main test runner."""
    print("🧪 MCP Server Integration Test Runner")
    print("=" * 50)
    
    # Check if user wants quick or full test
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        print("Running quick test suite...")
        result = await run_quick_test()
    else:
        print("Running comprehensive test suite...")
        result = await run_full_test_suite()
        result = result["success"]
    
    print("\n" + "=" * 50)
    if result:
        print("🎉 All tests completed successfully!")
        print("✅ MCP Server is ready for production use.")
    else:
        print("⚠️ Some tests failed.")
        print("❌ Please review the test output above.")
    
    return result


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        sys.exit(1)
