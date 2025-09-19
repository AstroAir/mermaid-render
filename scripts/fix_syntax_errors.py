from typing import Any
#!/usr/bin/env python3
"""
Script to fix specific syntax errors introduced by the annotation script.
"""

import os
import re
from pathlib import Path


def fix_syntax_errors(content: str) -> str:
    """Fix specific syntax error patterns."""
    
    # Fix patterns like: mock_svg = '<svg: Any xmlns="...">'
    content = re.sub(r"= '<svg: Any ", r"= '<svg ", content)
    
    # Fix patterns like: mock_response = Mock(: Any)
    content = re.sub(r"= Mock\(: Any\)", r"= Mock()", content)
    
    # Fix patterns like: mock_response.text =: Any mock_svg
    content = re.sub(r"\.([^=]+) =: Any ", r".\1 = ", content)
    
    # Fix patterns like: assert mock_get.call_count ==: Any 1
    content = re.sub(r"== Any ", r"== ", content)
    
    # Fix patterns like: os.path.join(temp_dir: Any, 'test.svg')
    content = re.sub(r"temp_dir: Any", r"temp_dir", content)
    
    # Fix patterns like: result.startswith(<newline>or: Any
    content = re.sub(r" or: Any ", r" or ", content)
    
    # Fix patterns like: assert ... or: Any result.startswith
    content = re.sub(r"\bor: Any\b", r"or", content)
    
    # Fix patterns like: # No additional: Any request
    content = re.sub(r"# No additional: Any", r"# No additional", content)
    
    return content


def process_file(file_path: Path) -> bool:
    """Process a single file to fix syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix syntax errors
        content = fix_syntax_errors(content)
        
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
    
    # Find all Python test files
    test_files = []
    for root, dirs, files in os.walk(str(root_dir / 'tests')):
        for file in files:
            if file.endswith('.py'):
                test_files.append(Path(root) / file)
    
    modified_count = 0
    for test_file in test_files:
        if process_file(test_file):
            modified_count += 1
            print(f"Fixed: {test_file}")
    
    print(f"\nProcessed {len(test_files)} files, fixed {modified_count}")


if __name__ == '__main__':
    main()
