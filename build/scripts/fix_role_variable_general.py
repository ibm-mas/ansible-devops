#!/usr/bin/env python3
"""
Fix Role Variables General Section Header

This script fixes README files where "## Role Variables" is used as the first
section header but there are also subgroup headers like "## Role Variables - X".
In these cases, the first section should be "## Role Variables - General".

Usage:
    python3 build/scripts/fix_role_variable_general.py ibm/mas_devops/roles/role_name/README.md
    python3 build/scripts/fix_role_variable_general.py ibm/mas_devops/roles --all
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple


def fix_role_variable_general(content: str) -> Tuple[str, List[str]]:
    """
    Fix "## Role Variables" to "## Role Variables - General" when subgroups exist.
    
    Only applies when:
    1. There's a "## Role Variables" header (without suffix)
    2. There are also "## Role Variables - X" headers (subgroups)
    
    Returns:
        Tuple of (fixed_content, list_of_fixes)
    """
    fixes = []
    lines = content.split('\n')
    
    # First pass: check if we have both patterns
    has_plain_role_variables = False
    has_role_variables_subgroups = False
    plain_role_variables_line = -1
    
    for i, line in enumerate(lines):
        if line.strip() == "## Role Variables":
            has_plain_role_variables = True
            plain_role_variables_line = i
        elif re.match(r'^## Role Variables - .+$', line.strip()):
            has_role_variables_subgroups = True
    
    # Only fix if both conditions are met
    if not (has_plain_role_variables and has_role_variables_subgroups):
        return content, fixes
    
    # Second pass: fix the plain "## Role Variables" header
    fixed_lines = []
    for i, line in enumerate(lines):
        if i == plain_role_variables_line:
            fixed_line = "## Role Variables - General"
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
    
    fixed_content, fixes = fix_role_variable_general(content)
    
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
        description='Fix Role Variables section to use "General" when subgroups exist'
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
