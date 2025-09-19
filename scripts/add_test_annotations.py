#!/usr/bin/env python3
"""
Script to automatically add missing function type annotations to test files.
This handles the most common cases where test functions are missing return
type annotations or parameter type annotations.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Any


def find_test_files(root_dir: str) -> List[Path]:
    """Find all Python test files."""
    test_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(Path(root) / file)
    return test_files


def add_return_annotations(content: str) -> str:
    """Add -> None annotations to functions missing return annotations."""
    lines = content.split('\n')
    result_lines = []
    
    for i, line in enumerate(lines):
        # Pattern for function definitions without return annotations
        func_match = re.match(r'^(\s*def\s+[^(]+\([^)]*\))\s*:\s*$', line)
        if func_match:
            # Check if this is a test function or should get -> None
            func_def = func_match.group(1)
            if ('test_' in func_def or 
                'def setup' in func_def or 
                'def teardown' in func_def or
                'def pytest' in func_def):
                # Add -> None annotation
                line = f"{func_def} -> None:"
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def add_parameter_annotations(content: str) -> str:
    """Add basic parameter annotations where obvious."""
    lines = content.split('\n')
    result_lines = []
    
    for line in lines:
        # Add type annotations for common patterns
        # mock parameters
        line = re.sub(r'\bmock_([^:,)]+)(?=[\s,)])', r'mock_\1: Any', line)
        # temp_dir parameters
        line = re.sub(r'\btemp_dir(?=[\s,)])', r'temp_dir: Any', line)
        # sample_* fixtures
        line = re.sub(r'\bsample_([^:,)]+)(?=[\s,)])', r'sample_\1: Any', line)
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def process_file(file_path: Path) -> bool:
    """Process a single file and add annotations."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add return annotations
        content = add_return_annotations(content)
        
        # Add parameter annotations
        content = add_parameter_annotations(content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        
    return False


def main() -> None:
    """Main function."""
    root_dir = Path(__file__).parent.parent
    test_files = find_test_files(str(root_dir / 'tests'))
    
    modified_count = 0
    for test_file in test_files:
        if process_file(test_file):
            modified_count += 1
            print(f"Modified: {test_file}")
    
    print(f"\nProcessed {len(test_files)} files, modified {modified_count}")


if __name__ == '__main__':
    main()
