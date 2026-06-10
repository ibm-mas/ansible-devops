#!/usr/bin/env python3
"""
Fix Role Variable Section Headers

This script fixes README files where "Role Variables - <subgroup>" headers
were incorrectly converted to plain text instead of H2 headers (##).

Usage:
    python3 build/scripts/fix_role_variable_headers.py ibm/mas_devops/roles/role_name/README.md
    python3 build/scripts/fix_role_variable_headers.py ibm/mas_devops/roles --all
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple


def fix_role_variable_headers(content: str) -> Tuple[str, List[str]]:
    """
    Fix Role Variables section headers that were incorrectly converted to plain text.
    
    Pattern to fix:
    - Plain text line: "Role Variables - <subgroup>"
    - Should be: "## Role Variables - <subgroup>"
    
    Returns:
        Tuple of (fixed_content, list_of_fixes)
    """
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    # Pattern to match lines that should be H2 headers
    # Matches: "Role Variables - <something>" at start of line (not already a header)
    pattern = r'^Role Variables - .+$'
    
    for i, line in enumerate(lines):
        # Skip if already a header
        if line.startswith('#'):
            fixed_lines.append(line)
            continue
            
        # Check if this line matches the pattern
        if re.match(pattern, line.strip()):
            # This is a "Role Variables - X" line that should be a header
            # Convert it to H2
            fixed_line = f"## {line.strip()}"
            fixed_lines.append(fixed_line)
            fixes.append(f"Line {i+1}: '{line.strip()}' -> '{fixed_line}'")
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes


def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Process a single README file.
    
    Returns:
        True if fixes were applied, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    fixed_content, fixes = fix_role_variable_headers(content)
    
    if not fixes:
        return False
    
    print(f"\n{'='*70}")
    print(f"Processing: {file_path}")
    print(f"{'='*70}")
    
    for fix in fixes:
        print(f"  ✓ {fix}")
    
    if not dry_run:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"\n✓ Applied {len(fixes)} fix(es) to {file_path.name}")
        except Exception as e:
            print(f"✗ Error writing file: {e}")
            return False
    else:
        print(f"\n[DRY RUN] Would apply {len(fixes)} fix(es)")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Fix Role Variables section headers in README files'
    )
    parser.add_argument(
        'path',
        help='Path to README.md file or roles directory'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all README.md files in the roles directory'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without making changes'
    )
    
    args = parser.parse_args()
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)
    
    files_to_process = []
    
    if args.all:
        if not path.is_dir():
            print("Error: --all requires a directory path")
            sys.exit(1)
        
        # Find all README.md files in role directories
        for role_dir in sorted(path.iterdir()):
            if role_dir.is_dir():
                readme = role_dir / 'README.md'
                if readme.exists():
                    files_to_process.append(readme)
    else:
        if path.is_file():
            files_to_process.append(path)
        else:
            readme = path / 'README.md'
            if readme.exists():
                files_to_process.append(readme)
            else:
                print(f"Error: No README.md found at {path}")
                sys.exit(1)
    
    if not files_to_process:
        print("No README.md files found to process")
        sys.exit(0)
    
    print(f"Processing {len(files_to_process)} file(s)...")
    if args.dry_run:
        print("[DRY RUN MODE - No changes will be made]\n")
    
    fixed_count = 0
    for file_path in files_to_process:
        if process_file(file_path, args.dry_run):
            fixed_count += 1
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total files processed: {len(files_to_process)}")
    print(f"Files with fixes: {fixed_count}")
    print(f"Files unchanged: {len(files_to_process) - fixed_count}")
    
    if args.dry_run:
        print("\n[DRY RUN] No changes were written to disk")
    else:
        print(f"\n✓ All fixes applied successfully")


if __name__ == '__main__':
    main()