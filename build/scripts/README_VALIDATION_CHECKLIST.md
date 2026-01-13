# README Validation Checklist

Use this checklist to validate README files for compliance with the standard template. This document also serves as a specification for the automated validation script.

## Automated Validation Script Specification

The validation script (`scripts/validate_readme.py`) should check the following:

### Script Usage
```bash
# Validate a single role
python scripts/validate_readme.py ibm/mas_devops/roles/role_name

# Validate all roles
python scripts/validate_readme.py ibm/mas_devops/roles --all

# Generate compliance report
python scripts/validate_readme.py ibm/mas_devops/roles --all --report
```

### Script Output
```
Validating: ibm/mas_devops/roles/role_name/README.md

✓ PASS: Title format correct
✗ FAIL: Decorative separator found after title (line 3)
✓ PASS: Description section present
✗ FAIL: Missing Example Playbook section
✓ PASS: License section present
✗ FAIL: Variable 'mas_instance_id' missing default value

Summary:
- Total Checks: 25
- Passed: 18
- Failed: 7
- Warnings: 2

Compliance Score: 72%
```

## Manual Validation Checklist

### 1. Title Section (Required)

- [ ] **Title uses single `#` (level 1 heading)**
  - ✅ Correct: `# role_name`
  - ❌ Incorrect: `## role_name`, `role_name\n=====`

- [ ] **Title matches role directory name**
  - Must be exact match (lowercase with underscores)
  - ✅ Correct: Directory `ibm_catalogs` → Title `# ibm_catalogs`
  - ❌ Incorrect: Directory `ibm_catalogs` → Title `# IBM Catalogs`

- [ ] **No decorative separators after title**
  - ❌ Remove: `=====`, `-----`, `___`

### 2. Description Section (Required)

- [ ] **Description immediately follows title**
  - No heading for description section
  - No blank lines between title and description

- [ ] **First paragraph is brief (1-2 sentences)**
  - Clear statement of what the role does
  - Starts with action verb

- [ ] **Additional paragraphs provide detail**
  - Key features explained
  - Important context provided
  - Integration points mentioned (if applicable)

### 3. Prerequisites Section (Conditional)

- [ ] **Section present if role has prerequisites**
  - External tools required
  - Credentials needed
  - Prior configuration required

- [ ] **Section omitted if no prerequisites**
  - Don't include empty Prerequisites section

- [ ] **Uses level 2 heading: `## Prerequisites`**

- [ ] **Uses bulleted list format**
  - Each prerequisite is clear and actionable
  - Links to installation guides included
  - Configuration methods specified

### 4. Role Variables Section (Required)

- [ ] **Uses level 2 heading: `## Role Variables`**

- [ ] **Variables organized into categories**
  - Uses level 3 headings (`###`) for categories
  - Logical grouping of related variables

- [ ] **Each variable properly documented**
  - Uses level 4 heading (`####`) for variable name
  - Clear description provided
  - Required/Optional status specified
  - Environment variable name included
  - Default value documented (or `None`)

#### Variable Documentation Format Check

For each variable, verify:

```markdown
#### variable_name
Description of the variable.

- **Required** or **Optional**
- Environment Variable: `ENV_VAR_NAME`
- Default Value: `value` or `None`
```

- [ ] **Variable name is level 4 heading**
- [ ] **Description is clear and complete**
- [ ] **Required/Optional status present**
- [ ] **Environment variable name present**
- [ ] **Default value present**

### 5. Example Playbook Section (Required)

- [ ] **Uses level 2 heading: `## Example Playbook`**

- [ ] **Standard introduction present**
  - "After installing the Ansible Collection you can include this role in your own custom playbooks."

- [ ] **YAML code block with language tag**
  - Uses ```yaml
  - Proper YAML formatting
  - Realistic example values

- [ ] **Example is complete and functional**
  - Shows common use case
  - Includes key required variables
  - Uses meaningful values (not just "value")

### 6. Run Role Playbook Section (Required)

- [ ] **Uses level 2 heading: `## Run Role Playbook`**

- [ ] **Standard introduction present**
  - "After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided."

- [ ] **Bash code block with language tag**
  - Uses ```bash
  - Shows environment variable exports
  - Shows ROLE_NAME command

- [ ] **Example matches Example Playbook section**
  - Same variables used
  - Same values shown
  - Consistent with playbook example

### 7. License Section (Required)

- [ ] **Uses level 2 heading: `## License`**

- [ ] **Content is `EPL-2.0`**

- [ ] **License section is last section**
  - No content after License section

## Formatting Checks

### Heading Hierarchy

- [ ] **No skipped heading levels**
  - Don't go from `##` to `####`
  - Maintain proper nesting

- [ ] **Consistent heading levels**
  - Level 1 (`#`): Title only
  - Level 2 (`##`): Main sections
  - Level 3 (`###`): Variable categories
  - Level 4 (`####`): Individual variables

### Code Blocks

- [ ] **All code blocks have language tags**
  - ✅ Correct: ```yaml, ```bash, ```json
  - ❌ Incorrect: ``` (no language)

- [ ] **YAML blocks use `yaml` tag**

- [ ] **Bash blocks use `bash` tag**

- [ ] **Code blocks are properly formatted**
  - Correct indentation
  - Valid syntax
  - No truncation

### Links

- [ ] **All links are valid**
  - Internal links point to existing files
  - External links are accessible

- [ ] **Internal links use relative paths**
  - ✅ Correct: `[mongodb](mongodb.md)`
  - ❌ Incorrect: `[mongodb](/full/path/mongodb.md)`

- [ ] **External links use full URLs**
  - Include protocol (https://)
  - Link to stable documentation

- [ ] **Link text is descriptive**
  - ✅ Correct: `[AWS CLI](url)`
  - ❌ Incorrect: `[click here](url)`

### Inline Code

- [ ] **Variable names use backticks**
  - Example: `mas_instance_id`

- [ ] **File names use backticks**
  - Example: `README.md`

- [ ] **Commands use backticks**
  - Example: `oc apply`

- [ ] **Values use backticks**
  - Example: `true`, `None`, `install`

### Lists

- [ ] **Bulleted lists use `-` (hyphen)**
  - Not `*` or `+`

- [ ] **Consistent indentation (2 spaces)**

- [ ] **No mixed list styles**

## Content Quality Checks

### Descriptions

- [ ] **Clear and concise**
  - No unnecessary jargon
  - Technical terms explained

- [ ] **Accurate and up-to-date**
  - Reflects current role behavior
  - No outdated information

- [ ] **Complete**
  - All features mentioned
  - Important limitations noted

### Variable Documentation

- [ ] **All variables documented**
  - No undocumented variables
  - Deprecated variables marked

- [ ] **Descriptions are helpful**
  - Explain purpose and usage
  - Note constraints or valid values
  - Mention relationships with other variables

- [ ] **Examples provided where helpful**
  - Complex values shown
  - Valid formats demonstrated

### Examples

- [ ] **Examples are realistic**
  - Use meaningful values
  - Show common use cases
  - Are copy-pasteable

- [ ] **Examples are tested**
  - Verified to work
  - No syntax errors
  - No missing variables

## Validation Scoring

### Compliance Levels

**100% - Fully Compliant**
- All required sections present
- All formatting correct
- All variables documented
- No issues found

**90-99% - Mostly Compliant**
- Minor formatting issues
- Small documentation gaps
- Easy fixes required

**75-89% - Partially Compliant**
- Missing some sections
- Inconsistent formatting
- Significant updates needed

**50-74% - Non-Compliant**
- Major sections missing
- Poor formatting
- Extensive rework required

**Below 50% - Severely Non-Compliant**
- Most sections missing
- No standard structure
- Complete rewrite needed

### Priority Scoring

Assign priority based on:
1. **Role importance** (core infrastructure vs. utility)
2. **Usage frequency** (commonly used vs. rarely used)
3. **Compliance score** (lower score = higher priority)

## Automated Validation Script Requirements

### Must Check

1. **File existence**: README.md exists in role directory
2. **Title format**: Single `#` with role name
3. **Decorative separators**: Detect and flag `=====`, `-----`
4. **Required sections**: All required sections present
5. **Heading levels**: Proper hierarchy maintained
6. **Code blocks**: All have language tags
7. **Variable format**: Each variable has required metadata
8. **Links**: All links are valid (basic check)

### Should Check

1. **Section order**: Sections in standard order
2. **Standard introductions**: Example sections use standard text
3. **Variable completeness**: All role variables documented
4. **Example validity**: Basic YAML/Bash syntax check
5. **Inline code**: Variable names use backticks

### Nice to Have

1. **Spelling**: Check for common typos
2. **Grammar**: Basic grammar checks
3. **Link accessibility**: Verify external links work
4. **Example testing**: Verify examples are functional
5. **Consistency**: Check consistency across similar roles

## Usage Examples

### Validating a Single Role

```bash
# Basic validation
python scripts/validate_readme.py ibm/mas_devops/roles/mongodb

# Verbose output
python scripts/validate_readme.py ibm/mas_devops/roles/mongodb --verbose

# Fix mode (auto-fix simple issues)
python scripts/validate_readme.py ibm/mas_devops/roles/mongodb --fix
```

### Validating Multiple Roles

```bash
# Validate all roles
python scripts/validate_readme.py ibm/mas_devops/roles --all

# Validate specific roles
python scripts/validate_readme.py ibm/mas_devops/roles/mongodb ibm/mas_devops/roles/db2

# Generate report
python scripts/validate_readme.py ibm/mas_devops/roles --all --report=report.html
```

### CI/CD Integration

```bash
# Exit with error if compliance < 90%
python scripts/validate_readme.py ibm/mas_devops/roles --all --min-score=90

# Check only changed files
python scripts/validate_readme.py $(git diff --name-only | grep README.md)
```

## Quick Reference

### Common Issues and Fixes

| Issue | Fix |
|-------|-----|
| Decorative separator after title | Remove `=====` or `-----` lines |
| Wrong heading level | Change `##` to `#` for title |
| Missing language tag | Add `yaml` or `bash` to code blocks |
| Missing variable metadata | Add Required/Optional, Env Var, Default |
| Missing Example Playbook | Add section with standard intro and example |
| Wrong section order | Reorder to match standard template |
| Missing License section | Add `## License\nEPL-2.0` at end |

### Validation Command Quick Reference

```bash
# Single role
python scripts/validate_readme.py ibm/mas_devops/roles/ROLE_NAME

# All roles
python scripts/validate_readme.py ibm/mas_devops/roles --all

# Generate report
python scripts/validate_readme.py ibm/mas_devops/roles --all --report

# Auto-fix simple issues
python scripts/validate_readme.py ibm/mas_devops/roles/ROLE_NAME --fix
```

---

**Note**: The validation script (`scripts/validate_readme.py`) should be created based on this specification. Until the script is available, use this checklist for manual validation.

**Last Updated**: 2026-01-12
**Version**: 1.0