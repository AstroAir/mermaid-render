from typing import Any
#!/usr/bin/env python3
"""
Enhanced script to fix all remaining ': Any' syntax errors that weren't caught by the previous script.
"""
import re
import os
from pathlib import Path

def fix_any_syntax_errors(file_path: str) -> bool:
    """Fix various ': Any' syntax errors in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix various patterns of invalid ': Any' usage
    patterns_to_fix = [
        # Function parameters with : Any
        (r'(\w+: Any)', r'\1'.replace(': Any', '')),
        # Mock calls with : Any
        (r'Mock\(: Any\)', 'Mock()'),
        # return_value with : Any
        (r'return_value="([^"]*): Any([^"]*)"', r'return_value="\1\2"'),
        # assert calls with : Any
        (r'\.assert_called_once\(: Any\)', '.assert_called_once()'),
        (r'\.assert_called_with\([^)]*: Any[^)]*\)', '.assert_called_with()'),
        # comparison operators with : Any
        (r'==: Any (\d+)', r'== \1'),
        (r'== ([^:]*): Any', r'== \1'),
        # Mock side effects with : Any
        (r'side_effect = \[([^]]*): Any([^]]*)\]', r'side_effect = [\1\2]'),
        # append calls with : Any
        (r'\.append\(([^)]*): Any\)', r'.append(\1)'),
        # Mock list items with : Any
        (r'\[Mock\(: Any\)\]', '[Mock()]'),
        # Variable assignments with : Any
        (r'= ([^=]*): Any([^=\n]*)', r'= \1\2'),
    ]
    
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content)
    
    # Additional specific fixes for common patterns
    content = re.sub(r'(\w+): Any(\s*[,\)])', r'\1\2', content)  # Function parameters
    content = re.sub(r': Any\s*\)', ')', content)  # Remove : Any before closing parentheses
    content = re.sub(r'f"([^"]*): Any([^"]*)"', r'f"\1\2"', content)  # f-strings
    content = re.sub(r'"([^"]*): Any([^"]*)"', r'"\1\2"', content)  # Regular strings
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main() -> None:
    """Main function to fix syntax errors in all Python files."""
    test_dir = Path('tests')
    files_fixed = 0
    
    for py_file in test_dir.rglob('*.py'):
        if fix_any_syntax_errors(str(py_file)):
            files_fixed += 1
            print(f"Fixed: {py_file}")
    
    print(f"\nFixed {files_fixed} files")

if __name__ == '__main__':
    main()
