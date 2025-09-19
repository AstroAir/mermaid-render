#!/usr/bin/env python3
"""
Script to remove unused type ignore comments based on mypy errors.
"""
import re
import subprocess
from pathlib import Path
from typing import List, Set, Dict

def get_unused_ignores() -> List[tuple]:
    """Get mypy errors about unused type ignore comments."""
    try:
        result = subprocess.run(
            ['mypy', '--show-error-codes', '.'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        unused_ignores = []
        for line in result.stdout.split('\n'):
            if 'Unused "type: ignore" comment' in line:
                # Parse: file:line: error: message
                match = re.match(r'([^:]+):(\d+): error:', line)
                if match:
                    file_path, line_num = match.groups()
                    file_path = file_path.replace('\\', '/')
                    unused_ignores.append((file_path, int(line_num)))
        return unused_ignores
    except FileNotFoundError:
        print("mypy not found. Please install mypy.")
        return []

def remove_unused_ignore(file_path: str, line_num: int) -> bool:
    """Remove unused type ignore comment from a specific line."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num > len(lines):
            return False
            
        line_idx = line_num - 1
        line = lines[line_idx]
        
        # Remove various forms of type ignore comments
        patterns = [
            r'\s*# type: ignore\[\w+-\w+\]',  # # type: ignore[error-code]
            r'\s*# type: ignore',             # # type: ignore
        ]
        
        new_line = line
        for pattern in patterns:
            new_line = re.sub(pattern, '', new_line)
        
        # Also clean up trailing whitespace
        new_line = new_line.rstrip() + '\n'
        
        if new_line != line:
            lines[line_idx] = new_line
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}:{line_num}: {e}")
        return False

def main() -> None:
    """Main function."""
    print("Getting unused type ignore comments...")
    unused_ignores = get_unused_ignores()
    
    if not unused_ignores:
        print("No unused type ignore comments found.")
        return
    
    fixes_made = 0
    
    # Group by file to avoid conflicts
    files_to_fix: Dict[str, List[int]] = {}
    for file_path, line_num in unused_ignores:
        if file_path not in files_to_fix:
            files_to_fix[file_path] = []
        files_to_fix[file_path].append(line_num)
    
    # Process each file
    for file_path, line_nums in files_to_fix.items():
        if Path(file_path).exists():
            # Sort line numbers in descending order to avoid index shifting
            for line_num in sorted(line_nums, reverse=True):
                if remove_unused_ignore(file_path, line_num):
                    fixes_made += 1
                    print(f"Removed unused ignore in {file_path}:{line_num}")
    
    print(f"\nTotal unused ignores removed: {fixes_made}")

if __name__ == '__main__':
    main()
