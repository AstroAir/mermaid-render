#!/usr/bin/env python3
"""
Script to fix missing parameter type annotations in test functions.
"""
import re
import subprocess
from pathlib import Path
from typing import List, Set, Dict, Any

def get_specific_errors() -> List[str]:
    """Get mypy errors about missing parameter annotations."""
    try:
        result = subprocess.run(
            ['mypy', '--show-error-codes', '.'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        return [line for line in result.stdout.split('\n') if 'Function is missing a type annotation for one or more arguments' in line]
    except FileNotFoundError:
        print("mypy not found. Please install mypy.")
        return []

def fix_parameter_annotations(file_path: str, line_num: int) -> bool:
    """Fix parameter annotations for a specific function."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num > len(lines):
            return False
            
        line_idx = line_num - 1
        line = lines[line_idx]
        
        # Skip if already has type annotations for parameters
        if ': ' in line and '->' in line:
            return False
        
        # Common patterns for test functions
        patterns = [
            # mock_* parameters
            (r'\b(mock_\w+)(?![:])', r'\1: Any'),
            # temp_dir, cache_dir parameters  
            (r'\b(temp_dir|cache_dir|output_dir)(?![:])', r'\1: Any'),
            # monkeypatch parameter
            (r'\b(monkeypatch)(?![:])', r'\1: Any'),
            # capsys, caplog parameters
            (r'\b(capsys|caplog)(?![:])', r'\1: Any'),
            # request parameter (pytest fixtures)
            (r'\b(request)(?![:])', r'\1: Any'),
        ]
        
        new_line = line
        modified = False
        
        for pattern, replacement in patterns:
            if re.search(pattern, new_line):
                new_line = re.sub(pattern, replacement, new_line)
                modified = True
        
        if modified:
            lines[line_idx] = new_line
            
            # Add Any import if needed
            has_any_import = any('from typing import' in line and 'Any' in line for line in lines)
            if not has_any_import:
                # Find existing typing import or add new one
                import_added = False
                for i, line in enumerate(lines):
                    if line.startswith('from typing import'):
                        if 'Any' not in line:
                            lines[i] = line.rstrip() + ', Any\n'
                            import_added = True
                            break
                
                if not import_added:
                    # Add new typing import after existing imports
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            insert_pos = i + 1
                        elif line.strip() == '' and insert_pos > 0:
                            break
                        elif not (line.startswith('#') or line.startswith('"""') or line.startswith("'''") or line.strip() == ''):
                            break
                    
                    lines.insert(insert_pos, 'from typing import Any\n')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}:{line_num}: {e}")
        return False

def main() -> None:
    """Main function."""
    print("Getting parameter annotation errors...")
    errors = get_specific_errors()
    
    if not errors:
        print("No parameter annotation errors found.")
        return
    
    fixes_made = 0
    
    for error in errors:
        # Parse error line: file:line: error: message
        match = re.match(r'([^:]+):(\d+): error:', error)
        if match:
            file_path, line_num = match.groups()
            file_path = file_path.replace('\\', '/')
            
            if Path(file_path).exists():
                if fix_parameter_annotations(file_path, int(line_num)):
                    fixes_made += 1
                    print(f"Fixed parameters in {file_path}:{line_num}")
    
    print(f"\nTotal fixes made: {fixes_made}")

if __name__ == '__main__':
    main()
