#!/usr/bin/env python3
"""
Improved script to add missing function type annotations based on mypy errors.
"""
import re
import subprocess
from pathlib import Path
from typing import List, Set, Dict, Any

def get_mypy_errors() -> List[str]:
    """Get mypy errors from the project."""
    try:
        result = subprocess.run(
            ['mypy', '--show-error-codes', '.'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        return result.stdout.split('\n')
    except FileNotFoundError:
        print("mypy not found. Please install mypy.")
        return []

def parse_annotation_errors(errors: List[str]) -> Dict[str, Set[int]]:
    """Parse mypy errors to find missing function annotations."""
    missing_annotations: Dict[str, Set[int]] = {}
    
    for error in errors:
        if 'Function is missing a type annotation' in error or 'Function is missing a return type annotation' in error:
            # Extract file and line number
            match = re.match(r'([^:]+):(\d+): error:', error)
            if match:
                file_path, line_num = match.groups()
                file_path = file_path.replace('\\', '/')
                
                if file_path not in missing_annotations:
                    missing_annotations[file_path] = set()
                missing_annotations[file_path].add(int(line_num))
    
    return missing_annotations

def fix_function_annotations(file_path: str, line_numbers: Set[int]) -> int:
    """Add missing function annotations to specific lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modifications = 0
        
        for line_num in sorted(line_numbers, reverse=True):
            if line_num <= len(lines):
                line_idx = line_num - 1
                line = lines[line_idx]
                
                # Skip if already has return annotation
                if '->' in line:
                    continue
                
                # Add return type annotation for test functions
                if re.search(r'def test_\w+\([^)]*\):', line):
                    lines[line_idx] = line.rstrip().rstrip(':') + ' -> None:\n'
                    modifications += 1
                
                # Add return type annotation for other functions without parameters
                elif re.search(r'def \w+\(\s*\):', line):
                    lines[line_idx] = line.rstrip().rstrip(':') + ' -> None:\n'
                    modifications += 1
                
                # Add basic parameter annotations for common patterns
                elif re.search(r'def \w+\([^)]*\):', line):
                    # Add return type annotation
                    new_line = line.rstrip().rstrip(':') + ' -> None:\n'
                    
                    # Simple parameter annotation for common patterns
                    new_line = re.sub(r'\b(mock_\w+)\b(?![:])', r'\1: Any', new_line)
                    new_line = re.sub(r'\b(temp_dir)\b(?![:])', r'\1: Any', new_line)
                    new_line = re.sub(r'\b(cache_dir)\b(?![:])', r'\1: Any', new_line)
                    
                    lines[line_idx] = new_line
                    modifications += 1
        
        if modifications > 0:
            # Add Any import if needed and not present
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
        
        return modifications
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main() -> None:
    """Main function."""
    print("Getting mypy errors...")
    errors = get_mypy_errors()
    
    if not errors:
        print("No mypy errors found or mypy not available.")
        return
    
    print("Parsing annotation errors...")
    missing_annotations = parse_annotation_errors(errors)
    
    if not missing_annotations:
        print("No missing annotation errors found.")
        return
    
    total_fixes = 0
    files_fixed = 0
    
    for file_path, line_numbers in missing_annotations.items():
        if Path(file_path).exists():
            fixes = fix_function_annotations(file_path, line_numbers)
            if fixes > 0:
                total_fixes += fixes
                files_fixed += 1
                print(f"Fixed {fixes} annotations in {file_path}")
    
    print(f"\nTotal: Fixed {total_fixes} annotations in {files_fixed} files")

if __name__ == '__main__':
    main()
