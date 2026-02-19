#!/usr/bin/env python3
"""
README Structure Fix Script for ibm.mas_devops Ansible Collection

This script automatically fixes common structural issues in README files:
- Converts decorative title separators to proper # format
- Adds missing Example Playbook sections
- Adds missing License sections
- Adds language tags to code blocks

Usage:
    python3 build/scripts/fix_readme_structure.py ibm/mas_devops/roles/role_name/README.md
    python3 build/scripts/fix_readme_structure.py ibm/mas_devops/roles --all
    python3 build/scripts/fix_readme_structure.py ibm/mas_devops/roles --all --dry-run
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple


class READMEFixer:
    """Fixes structural issues in README files"""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.fixes_applied = 0

    def fix_file(self, readme_path: Path) -> Tuple[bool, List[str]]:
        """Fix a single README file"""
        if not readme_path.exists():
            return False, [f"File does not exist: {readme_path}"]

        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                original_content = content
        except Exception as e:
            return False, [f"Error reading file: {str(e)}"]

        role_name = readme_path.parent.name
        fixes = []

        # Apply fixes
        content, title_fixes = self._fix_title_format(content, role_name)
        fixes.extend(title_fixes)

        content, separator_fixes = self._remove_decorative_separators(content)
        fixes.extend(separator_fixes)

        content, no_vars_fixes = self._add_no_variables_note(content, role_name)
        fixes.extend(no_vars_fixes)

        content, playbook_fixes = self._add_example_playbook(content, role_name)
        fixes.extend(playbook_fixes)

        content, license_fixes = self._add_license_section(content)
        fixes.extend(license_fixes)

        content, code_fixes = self._fix_code_blocks(content)
        fixes.extend(code_fixes)

        content, duplicate_fixes = self._remove_duplicate_sections(content)
        fixes.extend(duplicate_fixes)

        # Write back if changes were made
        if content != original_content:
            if not self.dry_run:
                try:
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.fixes_applied += 1
                    return True, fixes
                except Exception as e:
                    return False, [f"Error writing file: {str(e)}"]
            else:
                return True, fixes + ["[DRY RUN] Changes not written"]
        else:
            return True, ["No fixes needed"]

    def _fix_title_format(self, content: str, role_name: str) -> Tuple[str, List[str]]:
        """Fix title format to use # prefix"""
        lines = content.split('\n')
        fixes = []

        if not lines:
            return content, fixes

        first_line = lines[0].strip()

        # Check if first line is not a proper markdown heading
        if not first_line.startswith('#'):
            # Check if it's a title without # (common pattern)
            if first_line and not first_line.startswith('='):
                # Convert to proper heading
                lines[0] = f"# {first_line}"
                fixes.append(f"Fixed title format: '{first_line}' -> '# {first_line}'")
                content = '\n'.join(lines)

        return content, fixes

    def _remove_decorative_separators(self, content: str) -> Tuple[str, List[str]]:
        """Remove decorative separator lines (===, ---, etc.) and fix section headings"""
        lines = content.split('\n')
        fixes = []
        new_lines = []
        i = 0

        # Common section names that should be ## headings
        section_names = [
            'Role Variables', 'Example Playbook', 'License', 'Requirements',
            'Dependencies', 'Overview', 'Prerequisites', 'Usage', 'Notes'
        ]

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Check if line is a decorative separator
            if stripped and all(c in '=-_' for c in stripped) and len(stripped) >= 3:
                # Check if previous line is a section heading without ##
                if i > 0 and new_lines:
                    prev_line = new_lines[-1].strip()
                    if prev_line and not prev_line.startswith('#') and prev_line in section_names:
                        # Convert previous line to proper heading
                        new_lines[-1] = f"## {prev_line}"
                        fixes.append(f"Fixed section heading: '{prev_line}' -> '## {prev_line}'")
                
                # Skip the separator line
                fixes.append(f"Removed decorative separator at line {i+1}: {stripped[:50]}")
                i += 1
                continue

            # Check if this is a standalone section name that should be a heading
            if stripped in section_names and not stripped.startswith('#'):
                # Look ahead to see if next line is a separator
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and all(c in '=-_' for c in next_line) and len(next_line) >= 3:
                        # This is a section heading with separator - convert to ##
                        new_lines.append(f"## {stripped}")
                        fixes.append(f"Fixed section heading: '{stripped}' -> '## {stripped}'")
                        i += 2  # Skip both the heading and separator
                        continue
                
                # Standalone section heading without separator - still convert to ##
                new_lines.append(f"## {stripped}")
                fixes.append(f"Fixed section heading: '{stripped}' -> '## {stripped}'")
                i += 1
                continue

            new_lines.append(line)
            i += 1

        if fixes:
            content = '\n'.join(new_lines)

        return content, fixes

    def _add_example_playbook(self, content: str, role_name: str) -> Tuple[str, List[str]]:
        """Add Example Playbook section if missing"""
        fixes = []

        # Check if Example Playbook section exists
        if not re.search(r'^##\s+Example\s+Playbook', content, re.MULTILINE | re.IGNORECASE):
            # Find where to insert (before License section or at end)
            license_match = re.search(r'^##\s+License', content, re.MULTILINE | re.IGNORECASE)

            example_section = f"""
## Example Playbook

```yaml
- hosts: localhost
  vars:
    # Add required variables here
  roles:
    - ibm.mas_devops.{role_name}
```
"""

            if license_match:
                # Insert before License section
                insert_pos = license_match.start()
                content = content[:insert_pos] + example_section + '\n' + content[insert_pos:]
            else:
                # Append at end
                content = content.rstrip() + '\n' + example_section

            fixes.append("Added Example Playbook section")

        return content, fixes

    def _add_license_section(self, content: str) -> Tuple[str, List[str]]:
        """Add License section if missing or fix incorrect format"""
        fixes = []

        # Check if License section exists
        license_match = re.search(r'^##\s+License\s*$', content, re.MULTILINE)

        if not license_match:
            # Add License section at the end
            license_section = "\n## License\n\nEPL-2.0\n"
            content = content.rstrip() + '\n' + license_section
            fixes.append("Added License section")
        else:
            # Check if it has the correct content
            # Find the next section or end of file
            next_section = re.search(r'^##\s+', content[license_match.end():], re.MULTILINE)
            if next_section:
                license_content = content[license_match.end():license_match.end() + next_section.start()].strip()
            else:
                license_content = content[license_match.end():].strip()

            if license_content != "EPL-2.0":
                # Fix license content
                if next_section:
                    end_pos = license_match.end() + next_section.start()
                    content = content[:license_match.end()] + "\n\nEPL-2.0\n\n" + content[end_pos:]
                else:
                    content = content[:license_match.end()] + "\n\nEPL-2.0\n"
                fixes.append("Fixed License section content")

        return content, fixes

    def _fix_code_blocks(self, content: str) -> Tuple[str, List[str]]:
        """Code block fixes disabled - use report_missing_code_tags.py for manual fixes"""
        fixes = []
        # All code block logic disabled - manual fixes only
        return content, fixes
    
    def _remove_duplicate_sections(self, content: str) -> Tuple[str, List[str]]:
        """Remove duplicate sections (e.g., multiple License sections)"""
        fixes = []
        lines = content.split('\n')
        
        # Track sections we've seen
        seen_sections = {}
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this is a section heading
            if line.startswith('## '):
                section_name = line[3:].strip()
                
                if section_name in seen_sections:
                    # This is a duplicate - skip until next section or end
                    fixes.append(f"Removed duplicate section: {section_name}")
                    i += 1
                    # Skip content until next section
                    while i < len(lines) and not lines[i].strip().startswith('## '):
                        i += 1
                    continue
                else:
                    seen_sections[section_name] = True
            
            new_lines.append(lines[i])
            i += 1
        
        if fixes:
            content = '\n'.join(new_lines)
        
        return content, fixes
    
    def _add_no_variables_note(self, content: str, role_name: str) -> Tuple[str, List[str]]:
        """Add Role Variables section header or note for roles with no variables"""
        fixes = []
        
        # Check if Role Variables section exists
        role_vars_match = re.search(r'^##\s+Role\s+Variables\s*$', content, re.MULTILINE)
        
        if not role_vars_match:
            # No ## Role Variables section - check if there are any ### variable definitions
            first_var_match = re.search(r'^###\s+\w+', content, re.MULTILINE)
            
            if first_var_match:
                # Has variables but missing ## Role Variables header - add it before first variable
                insert_pos = first_var_match.start()
                content = content[:insert_pos] + "## Role Variables\n\n" + content[insert_pos:]
                fixes.append("Added missing '## Role Variables' section header before variable definitions")
            else:
                # No variables at all - add Role Variables section with note
                example_match = re.search(r'^##\s+Example\s+Playbook', content, re.MULTILINE)
                
                no_vars_section = """## Role Variables

This role has no configurable variables.

"""
                
                if example_match:
                    insert_pos = example_match.start()
                    content = content[:insert_pos] + no_vars_section + content[insert_pos:]
                else:
                    # Insert before License
                    license_match = re.search(r'^##\s+License', content, re.MULTILINE)
                    if license_match:
                        insert_pos = license_match.start()
                        content = content[:insert_pos] + no_vars_section + content[insert_pos:]
                
                fixes.append("Added Role Variables section with 'no variables' note")
        
        return content, fixes


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


def main():
    parser = argparse.ArgumentParser(
        description='Fix structural issues in README files'
    )
    parser.add_argument(
        'path',
        help='Path to README.md file or roles directory'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all README files in the directory'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without making changes'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )

    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    # Find README files to process
    if args.all:
        readme_files = find_readme_files(path)
        print(f"Found {len(readme_files)} README files to process\n")
    else:
        if path.is_file():
            readme_files = [path]
        else:
            readme_path = path / 'README.md'
            if readme_path.exists():
                readme_files = [readme_path]
            else:
                print(f"Error: README.md not found in {path}")
                sys.exit(1)

    # Process files
    fixer = READMEFixer(dry_run=args.dry_run, verbose=args.verbose)
    total_fixed = 0
    total_errors = 0

    for readme_path in readme_files:
        role_name = readme_path.parent.name
        print(f"Processing: {readme_path}")
        print("=" * 70)

        success, fixes = fixer.fix_file(readme_path)

        if success:
            if fixes and fixes != ["No fixes needed"]:
                total_fixed += 1
                print(f"✓ Fixed {len(fixes)} issue(s):")
                for fix in fixes:
                    print(f"  - {fix}")
            else:
                print("✓ No fixes needed")
        else:
            total_errors += 1
            print(f"✗ Error:")
            for error in fixes:
                print(f"  - {error}")

        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files processed: {len(readme_files)}")
    print(f"Files fixed: {total_fixed}")
    print(f"Errors: {total_errors}")

    if args.dry_run:
        print("\n[DRY RUN] No changes were written to disk")

    sys.exit(0 if total_errors == 0 else 1)


if __name__ == '__main__':
    main()
