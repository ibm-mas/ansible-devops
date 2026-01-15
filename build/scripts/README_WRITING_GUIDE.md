# README Writing Guide

This guide provides detailed instructions for writing and maintaining README files for roles in the `ibm.mas_devops` Ansible collection.

## Quick Start

1. Copy [`docs/templates/README_TEMPLATE.md`](templates/README_TEMPLATE.md) to your role directory as `README.md`
2. Replace placeholder text with role-specific content
3. Remove sections that don't apply (e.g., Prerequisites if none exist)
4. Review [`docs/templates/README_EXAMPLES.md`](templates/README_EXAMPLES.md) for concrete examples
5. Run validation script: `python scripts/validate_readme.py ibm/mas_devops/roles/your_role`

## Standard Structure

Every README must follow this structure:

```
# Title
Description
## Prerequisites (optional)
## Role Variables
### Category 1
#### variable_name
### Category 2
#### variable_name
## Example Playbook
## Run Role Playbook
## License
```

## Section-by-Section Guide

### 1. Title Section

**Format**: `# role_name`

**Rules**:
- Use single `#` (level 1 heading)
- Use exact role directory name (lowercase with underscores)
- No decorative separators (`=====` or `-----`)
- No additional formatting or styling

**Examples**:
```markdown
✅ CORRECT:
# ibm_catalogs

# mongodb

# suite_install

❌ INCORRECT:
# IBM Catalogs
=====

## ibm_catalogs

# ibm-catalogs
```

### 2. Description Section

**Position**: Immediately after title (no heading)

**Content Structure**:
1. **First paragraph**: Brief, clear description (1-2 sentences)
   - What the role does
   - Primary purpose

2. **Additional paragraphs**: Detailed explanation
   - Key features or capabilities
   - Important context or background
   - Integration points
   - Architectural notes

**Writing Tips**:
- Start with action verbs: "This role installs...", "This role configures...", "This role manages..."
- Be specific about what gets created/modified
- Mention important dependencies or relationships
- Include links to external documentation where relevant

**Example**:
```markdown
# mongodb
This role supports provisioning of MongoDB in three different providers: community, AWS DocumentDB, and IBM Cloud Database for MongoDB.

If the selected provider is `community`, then the MongoDB Community Kubernetes Operator will be configured and deployed into the specified namespace. By default, a three-member MongoDB replica set will be created. The cluster will bind six PVCs, providing persistence for the data and system logs across the three nodes.

The role will generate a YAML file containing the definition of a Secret and MongoCfg resource that can be used to configure the deployed instance as the MAS system MongoDB.
```

### 3. Prerequisites Section

**Heading**: `## Prerequisites` (level 2)

**When to Include**:
- External tools must be installed (CLI tools, utilities)
- Credentials or access must be configured
- Other resources must exist before running the role
- Specific environment setup is required

**When to Omit**:
- Role has no external dependencies
- Only requires standard Ansible/OpenShift setup

**Format**: Bulleted list with clear, actionable items

**Writing Tips**:
- Link to installation guides for tools
- Specify exact configuration methods
- Be explicit about what must be done before running the role
- Group related prerequisites together

**Example**:
```markdown
## Prerequisites
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) must be installed
- AWS credentials configured via `aws configure` command or by exporting `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables
- OpenShift cluster must be accessible via `oc` CLI
- Certificate Manager must be installed (see [`cert_manager`](cert_manager.md) role)
```

### 4. Role Variables Section

**Heading**: `## Role Variables` (level 2)

**Structure**:
```markdown
## Role Variables

### Category Name (level 3)
Brief description of this category if needed.

#### variable_name (level 4)
Description of the variable.

- **Required** or **Optional**
- Environment Variable: `ENV_VAR_NAME`
- Default Value: `value` or `None`
```

**Variable Categories**:

Organize variables into logical groups:
- **General Variables**: Common variables used across the role
- **Installation Variables**: Variables controlling installation behavior
- **Configuration Variables**: Variables for configuring the installed component
- **Advanced Configuration**: Optional advanced settings
- **Provider-Specific Variables**: Variables for specific providers (AWS, IBM Cloud, etc.)
- **Feature-Specific Variables**: Variables for optional features

**Variable Documentation Format**:

Each variable must include:

1. **Heading**: `#### variable_name` (level 4)
2. **Description**: Clear explanation of purpose and usage
3. **Required/Optional**: Explicitly state if required
4. **Environment Variable**: The environment variable name
5. **Default Value**: The default value or `None`

**Description Writing Tips**:
- Start with what the variable does
- Explain when/why to use it
- Note any constraints or valid values
- Mention relationships with other variables
- Include examples of valid values if helpful

**Example**:
```markdown
#### mongodb_storage_class
The name of the storage class to configure the MongoDB operator to use for persistent storage in the MongoDB cluster. Storage class must support ReadWriteOnce (RWO) access mode.

- **Required** when `mongodb_provider=community`
- Environment Variable: `MONGODB_STORAGE_CLASS`
- Default Value: None

#### mas_catalog_version
Version of the IBM Maximo Operator Catalog to install. Use `latest` to install the most recent version, or specify a specific version tag.

- **Optional**
- Environment Variable: `MAS_CATALOG_VERSION`
- Default Value: `v9-240625-amd64`

#### mongodb_action
Determines which action to perform with respect to MongoDB for a specified provider. Each provider supports a different set of actions:
- **community**: `install`, `uninstall`, `backup`, `restore`
- **aws**: `install`, `uninstall`, `docdb_secret_rotate`, `destroy-data`
- **ibm**: `install`, `uninstall`, `backup`, `restore`, `create-mongo-service-credentials`

- **Optional**
- Environment Variable: `MONGODB_ACTION`
- Default Value: `install`
```

**Common Mistakes to Avoid**:
- ❌ Missing Required/Optional status
- ❌ Missing environment variable name
- ❌ Missing default value
- ❌ Vague descriptions
- ❌ Inconsistent formatting
- ❌ Using level 3 headings for variables (should be level 4)

### 5. Example Playbook Section

**Heading**: `## Example Playbook` (level 2)

**Standard Introduction**:
"After installing the Ansible Collection you can include this role in your own custom playbooks."

**Format**: YAML code block with realistic example

**Content Guidelines**:
- Show a common, realistic use case
- Include key required variables
- Use meaningful example values (not just "value")
- Keep it concise but complete
- Use proper YAML formatting

**Example**:
```markdown
## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_catalog_source: ibm-operator-catalog
    mas_channel: 9.0.x
    mas_entitlement_key: "{{ lookup('env', 'IBM_ENTITLEMENT_KEY') }}"
  roles:
    - ibm.mas_devops.suite_install
```
```

### 6. Run Role Playbook Section

**Heading**: `## Run Role Playbook` (level 2)

**Standard Introduction**:
"After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided."

**Format**: Bash code block showing environment variable setup and command

**Content Guidelines**:
- Show how to set required environment variables
- Include the ROLE_NAME command
- Use realistic example values
- Match variables from Example Playbook section
- Keep it simple and copy-pasteable

**Example**:
```markdown
## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CATALOG_SOURCE=ibm-operator-catalog
export MAS_CHANNEL=9.0.x
export MAS_ENTITLEMENT_KEY=your_key_here
ROLE_NAME=suite_install ansible-playbook ibm.mas_devops.run_role
```
```

### 7. License Section

**Heading**: `## License` (level 2)

**Content**: `EPL-2.0`

**Position**: Always the last section

**Example**:
```markdown
## License
EPL-2.0
```

## Formatting Standards

### Headings

**Hierarchy**:
- `#` (Level 1): Title only
- `##` (Level 2): Main sections
- `###` (Level 3): Variable categories
- `####` (Level 4): Individual variables

**Rules**:
- No skipping levels (don't go from `##` to `####`)
- No decorative separators under headings
- Use sentence case for headings (not Title Case)
- Be consistent with heading text

### Code Blocks

**Always specify language**:
```markdown
✅ CORRECT:
```yaml
- hosts: localhost
```

```bash
export VAR=value
```

❌ INCORRECT:
```
- hosts: localhost
```
```

**Supported languages**:
- `yaml` - For Ansible playbooks and YAML files
- `bash` - For shell commands
- `json` - For JSON configuration
- `python` - For Python code

### Links

**Internal links** (to other roles):
```markdown
See the [`mongodb`](mongodb.md) role for details.
```

**External links**:
```markdown
Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
```

**Rules**:
- Use descriptive link text (not "click here")
- Verify all links are valid
- Use relative paths for internal links
- Use full URLs for external links

### Lists

**Bulleted lists**:
```markdown
- First item
- Second item
- Third item
```

**Nested lists**:
```markdown
- Parent item
  - Child item
  - Another child item
- Another parent item
```

**Rules**:
- Use `-` for bullets (not `*` or `+`)
- Maintain consistent indentation (2 spaces)
- Don't mix list styles

### Inline Code

Use backticks for:
- Variable names: `mas_instance_id`
- File names: `README.md`
- Commands: `oc apply`
- Values: `true`, `false`, `None`
- Environment variables: `MAS_INSTANCE_ID`

**Example**:
```markdown
Set `mas_instance_id` to your instance ID. The default value is `None`.
```

## Common Patterns

### Conditional Variables

When a variable is only required under certain conditions:

```markdown
#### db2_namespace
The namespace in your cluster that hosts the DB2 Warehouse instance. This will be used to lookup the Manage application database.

- **Optional** (Required when `mas_manage_attachment_configuration_mode=db`)
- Environment Variable: `DB2_NAMESPACE`
- Default Value: `db2u`
```

### Variables with Complex Values

For variables that accept complex values:

```markdown
#### mongodb_action
Determines which action to perform with respect to MongoDB for a specified provider.

Each provider supports a different set of actions:
- **community**: `install`, `uninstall`, `backup`, `restore`
- **aws**: `install`, `uninstall`, `docdb_secret_rotate`, `destroy-data`
- **ibm**: `install`, `uninstall`, `backup`, `restore`, `create-mongo-service-credentials`

- **Optional**
- Environment Variable: `MONGODB_ACTION`
- Default Value: `install`
```

### Deprecated Variables

For variables that are deprecated:

```markdown
#### sls_icr_cp
**[Deprecated in SLS 3.8.0]** The container registry source for all container images deployed by the SLS operator. Use `sls_icr_cpopen` instead for SLS 3.8.0 and later.

- **Optional**
- Environment Variable: `SLS_ICR_CP`
- Default Value: None
```

## Quality Checklist

Before submitting your README, verify:

### Structure
- [ ] Title uses single `#` with role name
- [ ] Description immediately follows title
- [ ] All sections use correct heading levels
- [ ] Sections appear in standard order
- [ ] License section is last

### Content
- [ ] Description is clear and complete
- [ ] Prerequisites listed (if applicable)
- [ ] All variables documented
- [ ] Each variable has Required/Optional status
- [ ] Each variable has Environment Variable name
- [ ] Each variable has Default Value
- [ ] Example Playbook is realistic and complete
- [ ] Run Role Playbook matches Example Playbook

### Formatting
- [ ] All code blocks have language tags
- [ ] All links are valid
- [ ] Inline code uses backticks
- [ ] Lists use consistent formatting
- [ ] No decorative separators

### Validation
- [ ] Run validation script passes
- [ ] No spelling errors
- [ ] No broken links
- [ ] Examples are tested and work

## Maintenance

### When to Update README

Update the README when:
- Adding new variables
- Changing variable behavior or defaults
- Adding new features or capabilities
- Deprecating variables or features
- Fixing errors or clarifying documentation
- Changing prerequisites

### Version Control

- Include README updates in the same PR as code changes
- Reference README changes in commit messages
- Review README changes as part of code review

### Testing

Before committing:
1. Run validation script
2. Test example playbook
3. Verify all links work
4. Check formatting in rendered view

## Getting Help

- Review [`README_EXAMPLES.md`](templates/README_EXAMPLES.md) for concrete examples
- Check existing well-formatted READMEs (e.g., `ibm_catalogs`, `aws_route53`)
- Ask questions in team channels
- Request review from documentation team

## Tools and Resources

### Validation Script
```bash
python scripts/validate_readme.py ibm/mas_devops/roles/your_role
```

### Template Files
- [`README_TEMPLATE.md`](templates/README_TEMPLATE.md) - Base template
- [`README_EXAMPLES.md`](templates/README_EXAMPLES.md) - Concrete examples

### Reference Documentation
- [Markdown Guide](https://www.markdownguide.org/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)

---

**Last Updated**: 2026-01-12
**Version**: 1.0