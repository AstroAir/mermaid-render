#!/usr/bin/env python3
"""
Script Verification Tool

This script verifies that all scripts in the scripts directory are properly
configured and can be imported without errors.

Usage:
    python scripts/verify-scripts.py
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def verify_script_syntax(script_path: Path) -> Tuple[bool, str]:
    """Verify that a script has valid Python syntax."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def check_script_imports(script_path: Path) -> Tuple[bool, str]:
    """Check if script imports can be resolved."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse imports
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Check if imports are available (basic check)
        problematic_imports = []
        for imp in imports:
            if imp.startswith('.'):  # Relative imports
                continue
            
            # Skip standard library and common packages
            if imp in ['os', 'sys', 'pathlib', 'subprocess', 'argparse', 'json', 
                      'time', 'datetime', 'typing', 'shutil', 'hashlib', 'sqlite3',
                      'statistics', 'cProfile', 'pstats', 'tracemalloc', 'io']:
                continue
            
            try:
                __import__(imp)
            except ImportError:
                problematic_imports.append(imp)
        
        if problematic_imports:
            return False, f"Missing imports: {', '.join(problematic_imports)}"
        
        return True, "OK"
    except Exception as e:
        return False, f"Error checking imports: {e}"


def verify_script_structure(script_path: Path) -> Tuple[bool, str]:
    """Verify script has proper structure."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Check for shebang
        if not content.startswith('#!/usr/bin/env python3'):
            issues.append("Missing shebang")
        
        # Check for docstring
        tree = ast.parse(content)
        if not ast.get_docstring(tree):
            issues.append("Missing module docstring")
        
        # Check for main function
        has_main = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'main':
                has_main = True
                break
        
        if not has_main:
            issues.append("Missing main() function")
        
        # Check for if __name__ == "__main__"
        has_main_guard = False
        for node in ast.walk(tree):
            if (isinstance(node, ast.If) and 
                isinstance(node.test, ast.Compare) and
                isinstance(node.test.left, ast.Name) and
                node.test.left.id == '__name__'):
                has_main_guard = True
                break
        
        if not has_main_guard:
            issues.append("Missing if __name__ == '__main__' guard")
        
        if issues:
            return False, f"Structure issues: {', '.join(issues)}"
        
        return True, "OK"
    except Exception as e:
        return False, f"Error checking structure: {e}"


def main():
    """Main verification function."""
    print("🔍 Verifying Scripts")
    print("=" * 50)
    
    scripts_dir = Path(__file__).parent
    python_scripts = list(scripts_dir.glob("*.py"))
    
    if not python_scripts:
        print("❌ No Python scripts found in scripts directory")
        return 1
    
    results = {}
    total_scripts = len(python_scripts)
    passed_scripts = 0
    
    for script_path in sorted(python_scripts):
        if script_path.name == 'verify-scripts.py':
            continue  # Skip self
        
        print(f"\n📝 Checking {script_path.name}...")
        
        script_results = {}
        
        # Check syntax
        syntax_ok, syntax_msg = verify_script_syntax(script_path)
        script_results['syntax'] = (syntax_ok, syntax_msg)
        print(f"  Syntax: {'✅' if syntax_ok else '❌'} {syntax_msg}")
        
        # Check imports
        imports_ok, imports_msg = check_script_imports(script_path)
        script_results['imports'] = (imports_ok, imports_msg)
        print(f"  Imports: {'✅' if imports_ok else '⚠️'} {imports_msg}")
        
        # Check structure
        structure_ok, structure_msg = verify_script_structure(script_path)
        script_results['structure'] = (structure_ok, structure_msg)
        print(f"  Structure: {'✅' if structure_ok else '⚠️'} {structure_msg}")
        
        # Overall status
        all_critical_ok = syntax_ok and imports_ok
        if all_critical_ok:
            passed_scripts += 1
            print(f"  Status: ✅ PASS")
        else:
            print(f"  Status: ❌ FAIL")
        
        results[script_path.name] = script_results
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 50)
    print(f"Total scripts checked: {total_scripts}")
    print(f"Scripts passed: {passed_scripts}")
    print(f"Scripts failed: {total_scripts - passed_scripts}")
    
    if passed_scripts == total_scripts:
        print("\n🎉 All scripts passed verification!")
        return 0
    else:
        print(f"\n⚠️ {total_scripts - passed_scripts} scripts have issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
