#!/usr/bin/env python3
"""
Report Code Blocks Missing Language Tags

This script identifies code blocks that are missing language tags
and reports their locations for manual fixing.

Usage:
    python3 build/scripts/report_missing_code_tags.py ibm/mas_devops/roles
    python3 build/scripts/report_missing_code_tags.py ibm/mas_devops/roles/role_name/README.md
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


def find_readme_files(base_path: Path) -> List[Path]:
    """Find all README.md files in role directories"""
    readme_files = []

    if base_path.is_file() and base_path.name == 'README.md':
        return [base_path]

    # Look for role directories
    if base_path.is_dir():
        for role_dir in sorted(base_path.iterdir()):
            if role_dir.is_dir():
                readme_path = role_dir / 'README.md'
                if readme_path.exists():
                    readme_files.append(readme_path)

    return readme_files


def find_missing_language_tags(readme_path: Path) -> List[Tuple[int, str]]:
    """Find code blocks missing language tags and return (line_number, next_line_preview)"""
    missing_tags = []
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {readme_path}: {e}", file=sys.stderr)
        return missing_tags
    
    in_code_block = False
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        
        # Check if this is a code fence (must be at start of line, possibly with leading whitespace)
        # Ignore ``` that appear in the middle of text or after other content
        if stripped.startswith('```') and stripped == '```' or (stripped.startswith('```') and len(stripped) > 3 and stripped[3:].strip() == ''):
            # This is a fence line (either ``` alone or ``` followed by whitespace)
            if not in_code_block:
                # This is an opening fence
                if stripped == '```':
                    # No language tag - check if this looks like a real code block
                    # Real code blocks have content on next line and eventually a closing fence
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        # Skip if next line is empty or looks like a list item (decorative use)
                        if next_line and not next_line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*')):
                            preview = next_line[:60]
                            missing_tags.append((i + 1, preview))  # Line numbers are 1-based
                in_code_block = True
            else:
                # This is a closing fence
                in_code_block = False
        
        i += 1
    
    return missing_tags


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 report_missing_code_tags.py <path>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)
    
    # Find README files
    readme_files = find_readme_files(path)
    
    if not readme_files:
        print("No README.md files found")
        sys.exit(0)
    
    print(f"Scanning {len(readme_files)} README files for code blocks missing language tags...\n")
    
    total_missing = 0
    files_with_issues = 0
    
    for readme_path in readme_files:
        missing_tags = find_missing_language_tags(readme_path)
        
        if missing_tags:
            files_with_issues += 1
            total_missing += len(missing_tags)
            
            # Print each missing tag location in format: filename:linenumber
            for line_num, preview in missing_tags:
                print(f"{readme_path}:{line_num}")
    
    # Summary to stderr
    print(f"\n# Files scanned: {len(readme_files)}", file=sys.stderr)
    print(f"# Files with missing tags: {files_with_issues}", file=sys.stderr)
    print(f"# Total code blocks missing language tags: {total_missing}", file=sys.stderr)
    
    if total_missing > 0:
        sys.exit(1)
    else:
        print("# ✅ All code blocks have language tags!", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
