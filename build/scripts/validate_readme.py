#!/usr/bin/env python3
"""
README Validation Script for ibm.mas_devops Ansible Collection

This script validates README files against the standard template defined in
docs/templates/README_TEMPLATE.md and docs/README_VALIDATION_CHECKLIST.md

Usage:
    python scripts/validate_readme.py ibm/mas_devops/roles/role_name
    python scripts/validate_readme.py ibm/mas_devops/roles --all
    python scripts/validate_readme.py ibm/mas_devops/roles --all --report
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Stores validation results for a README file"""
    role_name: str
    file_path: str
    exists: bool = True
    checks_passed: int = 0
    checks_failed: int = 0
    warnings: int = 0
    issues: List[str] = field(default_factory=list)
    warnings_list: List[str] = field(default_factory=list)

    @property
    def total_checks(self) -> int:
        return self.checks_passed + self.checks_failed

    @property
    def compliance_score(self) -> float:
        if self.total_checks == 0:
            return 0.0
        return (self.checks_passed / self.total_checks) * 100


class READMEValidator:
    """Validates README files against the standard template"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def validate_file(self, readme_path: Path) -> ValidationResult:
        """Validate a single README file"""
        role_name = readme_path.parent.name
        result = ValidationResult(role_name=role_name, file_path=str(readme_path))

        if not readme_path.exists():
            result.exists = False
            result.issues.append("README.md file does not exist")
            return result

        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            result.issues.append(f"Error reading file: {str(e)}")
            return result

        # Run all validation checks
        self._check_title_format(content, lines, result)
        self._check_decorative_separators(lines, result)
        self._check_required_sections(content, result)
        self._check_heading_hierarchy(lines, result)
        self._check_variable_documentation(content, lines, result)
        self._check_code_blocks(content, lines, result)
        self._check_license_section(content, result)

        return result

    def _check_title_format(self, content: str, lines: List[str], result: ValidationResult):
        """Check if title uses correct format: # role_name"""
        if not lines:
            result.checks_failed += 1
            result.issues.append("File is empty")
            return

        first_line = lines[0].strip()

        # Check if starts with single #
        if first_line.startswith('# '):
            result.checks_passed += 1

            # Check if matches role name
            title_text = first_line[2:].strip()
            if title_text.lower() != result.role_name.lower():
                result.warnings += 1
                result.warnings_list.append(
                    f"Title '{title_text}' doesn't match role name '{result.role_name}'"
                )
        else:
            result.checks_failed += 1
            if first_line.startswith('##'):
                result.issues.append("Title uses ## instead of # (line 1)")
            elif not first_line.startswith('#'):
                result.issues.append("Title doesn't start with # (line 1)")
            else:
                result.issues.append("Title format incorrect (line 1)")

    def _check_decorative_separators(self, lines: List[str], result: ValidationResult):
        """Check for decorative separators like ===== or -----"""
        separator_patterns = [
            r'^={3,}$',  # ===
            r'^-{3,}$',  # ---
            r'^_{3,}$',  # ___
        ]

        found_separator = False
        for i, line in enumerate(lines[:10], 1):  # Check first 10 lines
            line = line.strip()
            for pattern in separator_patterns:
                if re.match(pattern, line):
                    result.checks_failed += 1
                    result.issues.append(f"Decorative separator found (line {i}): {line}")
                    found_separator = True
                    break

        if not found_separator:
            result.checks_passed += 1

    def _check_required_sections(self, content: str, result: ValidationResult):
        """Check for required sections"""
        required_sections = {
            'Role Variables': r'##\s+Role Variables',
            'Example Playbook': r'##\s+Example Playbook',
            'License': r'##\s+License',
        }

        for section_name, pattern in required_sections.items():
            if re.search(pattern, content, re.MULTILINE):
                result.checks_passed += 1
            else:
                result.checks_failed += 1
                result.issues.append(f"Missing required section: {section_name}")

    def _check_heading_hierarchy(self, lines: List[str], result: ValidationResult):
        """Check heading hierarchy is correct"""
        heading_pattern = r'^(#{1,6})\s+'
        prev_level = 0
        issues_found = False

        for i, line in enumerate(lines, 1):
            match = re.match(heading_pattern, line)
            if match:
                current_level = len(match.group(1))

                # Check for skipped levels (e.g., ## to ####)
                if prev_level > 0 and current_level > prev_level + 1:
                    result.warnings += 1
                    result.warnings_list.append(
                        f"Skipped heading level from {prev_level} to {current_level} (line {i})"
                    )
                    issues_found = True

                prev_level = current_level

        if not issues_found:
            result.checks_passed += 1
        else:
            result.checks_failed += 1

    def _check_variable_documentation(self, content: str, lines: List[str], result: ValidationResult):
        """Check if variables are properly documented"""
        # Find all level 4 headings (variables)
        variable_pattern = r'^####\s+(\w+)'
        variables_found = []

        for i, line in enumerate(lines):
            match = re.match(variable_pattern, line)
            if match:
                var_name = match.group(1)
                variables_found.append((var_name, i))

        if not variables_found:
            # No variables documented, which might be OK for some roles
            result.warnings += 1
            result.warnings_list.append("No variables documented (might be intentional)")
            return

        # Check each variable has required metadata
        incomplete_vars = []
        for var_name, line_num in variables_found:
            # Get next 10 lines after variable heading
            var_section = '\n'.join(lines[line_num:line_num+10])

            has_required = 'Required' in var_section or 'Optional' in var_section
            has_env_var = 'Environment Variable:' in var_section
            has_default = 'Default Value:' in var_section or 'Default:' in var_section

            if not (has_required and has_env_var and has_default):
                missing = []
                if not has_required:
                    missing.append('Required/Optional')
                if not has_env_var:
                    missing.append('Environment Variable')
                if not has_default:
                    missing.append('Default Value')
                incomplete_vars.append(f"{var_name} (missing: {', '.join(missing)})")

        if incomplete_vars:
            result.checks_failed += 1
            result.issues.append(
                f"Variables with incomplete documentation: {', '.join(incomplete_vars[:3])}"
                + (f" and {len(incomplete_vars)-3} more" if len(incomplete_vars) > 3 else "")
            )
        else:
            result.checks_passed += 1

    def _check_code_blocks(self, content: str, lines: List[str], result: ValidationResult):
        """Check if code blocks have language tags"""
        code_block_start_pattern = r'^```(\w*)$'
        blocks_without_lang = []
        in_code_block = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('```'):
                if not in_code_block:
                    # This is an opening code block
                    match = re.match(code_block_start_pattern, stripped)
                    if match:
                        lang = match.group(1)
                        if not lang:
                            blocks_without_lang.append(i)
                    in_code_block = True
                else:
                    # This is a closing code block
                    in_code_block = False

        if blocks_without_lang:
            result.checks_failed += 1
            result.issues.append(
                f"Code blocks without language tags (lines: {', '.join(map(str, blocks_without_lang[:5]))})"
            )
        else:
            result.checks_passed += 1

    def _check_license_section(self, content: str, result: ValidationResult):
        """Check if License section exists and is last"""
        license_pattern = r'##\s+License\s*\n+EPL-2\.0'

        if re.search(license_pattern, content):
            result.checks_passed += 1

            # Check if it's at the end
            lines = content.strip().split('\n')
            last_lines = '\n'.join(lines[-5:])
            if 'License' not in last_lines:
                result.warnings += 1
                result.warnings_list.append("License section should be last")
        else:
            result.checks_failed += 1
            result.issues.append("Missing or incorrect License section (should be '## License' followed by 'EPL-2.0')")

    def print_result(self, result: ValidationResult):
        """Print validation result"""
        print(f"\nValidating: {result.file_path}")
        print("=" * 70)

        if not result.exists:
            print("[FAIL] README.md file does not exist")
            return

        # Print issues
        if result.issues:
            print("\n[FAILED CHECKS]:")
            for issue in result.issues:
                print(f"  - {issue}")

        # Print warnings
        if result.warnings_list:
            print("\n[WARNINGS]:")
            for warning in result.warnings_list:
                print(f"  - {warning}")

        # Print summary
        print(f"\n[SUMMARY]:")
        print(f"  Total Checks: {result.total_checks}")
        print(f"  Passed: {result.checks_passed}")
        print(f"  Failed: {result.checks_failed}")
        print(f"  Warnings: {result.warnings}")
        print(f"  Compliance Score: {result.compliance_score:.1f}%")

        if result.compliance_score == 100 and result.warnings == 0:
            print("\n[EXCELLENT] README is fully compliant!")
        elif result.compliance_score >= 90:
            print("\n[GOOD] README is mostly compliant")
        elif result.compliance_score >= 75:
            print("\n[FAIR] README needs some improvements")
        else:
            print("\n[POOR] README needs significant improvements")


def find_all_roles(roles_dir: Path) -> List[Path]:
    """Find all role directories with README files"""
    roles = []
    if not roles_dir.exists():
        return roles

    for item in roles_dir.iterdir():
        if item.is_dir():
            readme_path = item / 'README.md'
            roles.append(readme_path)

    return sorted(roles)


def generate_report(results: List[ValidationResult], output_file: str | None = None):
    """Generate a summary report"""
    total_roles = len(results)
    roles_with_readme = sum(1 for r in results if r.exists)
    fully_compliant = sum(1 for r in results if r.compliance_score == 100 and r.warnings == 0)
    mostly_compliant = sum(1 for r in results if 90 <= r.compliance_score < 100)
    needs_work = sum(1 for r in results if r.compliance_score < 90)

    avg_score = sum(r.compliance_score for r in results) / total_roles if total_roles > 0 else 0

    report = f"""
README Validation Report
{'=' * 70}

Overall Statistics:
  Total Roles: {total_roles}
  Roles with README: {roles_with_readme} ({roles_with_readme/total_roles*100:.1f}%)
  Average Compliance Score: {avg_score:.1f}%

Compliance Breakdown:
  Fully Compliant (100%): {fully_compliant}
  Mostly Compliant (90-99%): {mostly_compliant}
  Needs Improvement (<90%): {needs_work}
  Missing README: {total_roles - roles_with_readme}

Roles Needing Attention:
"""

    # List roles with low compliance
    low_compliance = sorted(
        [r for r in results if r.exists and r.compliance_score < 90],
        key=lambda x: x.compliance_score
    )

    for result in low_compliance[:10]:
        report += f"  - {result.role_name}: {result.compliance_score:.1f}% ({result.checks_failed} issues)\n"

    if len(low_compliance) > 10:
        report += f"  ... and {len(low_compliance) - 10} more\n"

    # List roles without README
    missing_readme = [r for r in results if not r.exists]
    if missing_readme:
        report += "\nRoles Missing README:\n"
        for result in missing_readme:
            report += f"  - {result.role_name}\n"

    print(report)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate README files for ibm.mas_devops roles'
    )
    parser.add_argument(
        'path',
        help='Path to role directory or roles parent directory'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all roles in the directory'
    )
    parser.add_argument(
        '--report',
        nargs='?',
        const='readme_validation_report.txt',
        help='Generate summary report (optionally specify output file)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--min-score',
        type=float,
        default=0,
        help='Minimum compliance score required (exit with error if below)'
    )

    args = parser.parse_args()

    path = Path(args.path)
    validator = READMEValidator(verbose=args.verbose)
    results = []

    if args.all:
        # Validate all roles
        readme_files = find_all_roles(path)
        print(f"Found {len(readme_files)} roles to validate\n")

        for readme_path in readme_files:
            result = validator.validate_file(readme_path)
            results.append(result)
            if not args.report:  # Only print individual results if not generating report
                validator.print_result(result)

        if args.report:
            generate_report(results, args.report if isinstance(args.report, str) else None)
    else:
        # Validate single role
        readme_path = path / 'README.md' if path.is_dir() else path
        result = validator.validate_file(readme_path)
        results.append(result)
        validator.print_result(result)

    # Check minimum score requirement
    if args.min_score > 0:
        failing_roles = [r for r in results if r.exists and r.compliance_score < args.min_score]
        if failing_roles:
            print(f"\n❌ ERROR: {len(failing_roles)} role(s) below minimum score of {args.min_score}%")
            sys.exit(1)

    # Exit with error if any validation failed
    if any(r.checks_failed > 0 or not r.exists for r in results):
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
