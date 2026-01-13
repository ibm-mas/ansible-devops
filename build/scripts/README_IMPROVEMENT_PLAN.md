# README Improvement Plan for Ansible DevOps Collection

## Executive Summary

This document outlines a comprehensive plan to improve the quality and consistency of README files across all roles in the `ibm.mas_devops` Ansible collection. The focus is on establishing structural consistency through standardized formatting, section ordering, and heading styles.

## Current State Analysis

### Identified Inconsistencies

After analyzing README files across 80+ roles, the following major inconsistencies were identified:

#### 1. **Title Formatting Variations**
- **Inconsistent heading levels**: Some use `# role_name`, others use `role_name` with underlines (`===`)
- **Mixed capitalization**: "AI Service" vs "aws_route53" vs "suite_dns"
- **Examples**:
  - [`aiservice/README.md`](ibm/mas_devops/roles/aiservice/README.md:1): Uses `# AI Service` followed by `=====`
  - [`ibm_catalogs/README.md`](ibm/mas_devops/roles/ibm_catalogs/README.md:1): Uses `# ibm_catalogs`
  - [`aws_route53/README.md`](ibm/mas_devops/roles/aws_route53/README.md:1): Uses `aws_route53` with `=========`

#### 2. **Section Ordering Variations**
Different roles present information in different orders:
- Some start with description, others with prerequisites
- Variable sections appear at different positions
- Example playbooks sometimes before, sometimes after variables
- License section placement varies

#### 3. **Heading Style Inconsistencies**
- **Mixed heading levels**: Some use `##`, others use `###` for the same type of content
- **Inconsistent section names**:
  - "Role Variables" vs "Variables" vs "Role Variables - General"
  - "Example Playbook" vs "Example" vs "Usage"
  - "Prerequisites" vs "Pre-requisites" vs missing entirely

#### 4. **Variable Documentation Variations**
- **Inconsistent formatting**:
  - Some use `### variable_name` headings
  - Others use bold text `**variable_name**`
  - Mixed use of bullet points vs paragraphs
- **Incomplete metadata**:
  - Environment variable names sometimes missing
  - Default values not always specified
  - Required/Optional status inconsistent

#### 5. **Missing or Incomplete Sections**
- Many roles lack Prerequisites sections
- License information missing or inconsistent
- Run Role Playbook examples absent in some files
- No consistent pattern for advanced configuration

## Proposed Standard Structure

### Template Overview

```markdown
# role_name
Brief one-line description of what the role does.

Detailed description paragraph(s) explaining the role's purpose, key features,
and any important context users should know.

## Prerequisites
List of requirements that must be met before using this role:
- Software dependencies
- Access requirements
- Configuration prerequisites

## Role Variables

### General Variables
Variables that apply broadly to the role.

#### variable_name
Description of what this variable does and when to use it.

- **Required/Optional**
- Environment Variable: `ENV_VAR_NAME`
- Default Value: `default_value`

### Category-Specific Variables
Group related variables under descriptive category headings.

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    variable_name: value
  roles:
    - ibm.mas_devops.role_name
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export ENV_VAR_NAME=value
ROLE_NAME=role_name ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
```

### Detailed Section Guidelines

#### 1. **Title Section**
- **Format**: `# role_name` (single `#`, no underlines)
- **Naming**: Use the actual role directory name (lowercase with underscores)
- **No decorative separators**: Remove `=====` or `---` lines

#### 2. **Description Section**
- **Position**: Immediately after title
- **Content**:
  - First paragraph: Brief, clear description (1-2 sentences)
  - Additional paragraphs: Detailed explanation, key features, important notes
- **No heading**: Description flows directly after title

#### 3. **Prerequisites Section**
- **Heading**: `## Prerequisites` (level 2)
- **When to include**: If role requires external tools, access, or prior setup
- **Format**: Bulleted list with clear, actionable items
- **Example**:
  ```markdown
  ## Prerequisites
  - [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) must be installed
  - AWS credentials configured via `aws configure` or environment variables
  - OpenShift cluster must be accessible via `oc` CLI
  ```

#### 4. **Role Variables Section**
- **Heading**: `## Role Variables` (level 2)
- **Subsections**: Use level 3 headings (`###`) for variable categories
- **Variable documentation**: Use level 4 headings (`####`) for each variable

**Variable Documentation Format**:
```markdown
#### variable_name
Clear description of the variable's purpose and usage.

- **Required** or **Optional**
- Environment Variable: `ENV_VAR_NAME`
- Default Value: `value` or `None`
```

**Category Organization**:
- Group related variables under descriptive category headings
- Common categories:
  - General Variables
  - Installation Variables
  - Configuration Variables
  - Advanced Configuration
  - Provider-Specific Variables (AWS, IBM Cloud, etc.)

#### 5. **Example Playbook Section**
- **Heading**: `## Example Playbook` (level 2)
- **Standard introduction**: "After installing the Ansible Collection you can include this role in your own custom playbooks."
- **Format**: YAML code block with realistic example
- **Content**: Show common use case with key variables

#### 6. **Run Role Playbook Section**
- **Heading**: `## Run Role Playbook` (level 2)
- **Standard introduction**: "After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided."
- **Format**: Bash code block showing environment variable setup and command
- **Content**: Demonstrate standalone execution

#### 7. **License Section**
- **Heading**: `## License` (level 2)
- **Content**: `EPL-2.0` (consistent across all roles)
- **Position**: Always last section

## Implementation Plan

### Phase 1: Template Creation and Documentation (Week 1)
1. Create official README template file
2. Document template usage guidelines
3. Create examples for common role types
4. Review and approve template with team

### Phase 2: Validation Tools (Week 2)
1. Create README validation script to check:
   - Heading structure compliance
   - Required sections presence
   - Variable documentation format
   - Code block formatting
2. Integrate validation into CI/CD pipeline
3. Generate compliance report for existing READMEs

### Phase 3: Prioritized Updates (Weeks 3-6)
Update READMEs in priority order:

**Priority 1 - Core Infrastructure Roles** (Week 3):
- [`ibm_catalogs`](ibm/mas_devops/roles/ibm_catalogs)
- [`cert_manager`](ibm/mas_devops/roles/cert_manager)
- [`mongodb`](ibm/mas_devops/roles/mongodb)
- [`db2`](ibm/mas_devops/roles/db2)
- [`sls`](ibm/mas_devops/roles/sls)

**Priority 2 - Suite Installation Roles** (Week 4):
- [`suite_install`](ibm/mas_devops/roles/suite_install)
- [`suite_config`](ibm/mas_devops/roles/suite_config)
- [`suite_dns`](ibm/mas_devops/roles/suite_dns)
- [`suite_verify`](ibm/mas_devops/roles/suite_verify)

**Priority 3 - Application Roles** (Week 5):
- [`suite_app_install`](ibm/mas_devops/roles/suite_app_install)
- [`suite_app_config`](ibm/mas_devops/roles/suite_app_config)
- [`suite_app_upgrade`](ibm/mas_devops/roles/suite_app_upgrade)

**Priority 4 - Remaining Roles** (Week 6):
- All other roles in alphabetical order

### Phase 4: Review and Quality Assurance (Week 7)
1. Peer review of updated READMEs
2. User testing with sample documentation
3. Address feedback and make corrections
4. Final validation run

### Phase 5: Documentation and Training (Week 8)
1. Update contributor guidelines
2. Create README writing guide
3. Conduct team training session
4. Establish ongoing maintenance process

## Validation Checklist

Use this checklist to verify README compliance:

### Structure
- [ ] Title uses single `#` with role name (no decorative separators)
- [ ] Description immediately follows title (no heading)
- [ ] All sections use consistent heading levels (## for main, ### for sub)
- [ ] Sections appear in standard order

### Required Sections
- [ ] Title and description present
- [ ] Prerequisites section (if applicable)
- [ ] Role Variables section with proper formatting
- [ ] Example Playbook section with standard intro
- [ ] Run Role Playbook section with standard intro
- [ ] License section (EPL-2.0)

### Variable Documentation
- [ ] Each variable has level 4 heading (`####`)
- [ ] Clear description provided
- [ ] Required/Optional status specified
- [ ] Environment variable name included
- [ ] Default value documented
- [ ] Variables grouped into logical categories

### Code Blocks
- [ ] All code blocks properly fenced with language tags
- [ ] YAML examples use `yaml` tag
- [ ] Bash examples use `bash` tag
- [ ] Examples are realistic and functional

### Links and References
- [ ] Internal role references use relative links
- [ ] External links use full URLs
- [ ] All links are valid and accessible

## Roles Requiring Immediate Attention

Based on analysis, these roles have significant README issues:

### Missing README Files
- [`minio`](ibm/mas_devops/roles/minio) - No README.md found
- [`nvidia_gpu`](ibm/mas_devops/roles/nvidia_gpu) - No README.md found

### Severely Incomplete READMEs
- [`aiservice`](ibm/mas_devops/roles/aiservice/README.md) - Missing examples, inconsistent formatting
- [`aiservice_tenant`](ibm/mas_devops/roles/aiservice_tenant/README.md) - Unusual structure with `=====`
- [`suite_manage_pvc_config`](ibm/mas_devops/roles/suite_manage_pvc_config/README.md) - Missing example playbook

### Inconsistent Structure
- [`suite_dns`](ibm/mas_devops/roles/suite_dns/README.md) - Mixed heading levels, complex structure
- [`cp4d`](ibm/mas_devops/roles/cp4d/README.md) - Good content but inconsistent formatting
- [`ocp_provision`](ibm/mas_devops/roles/ocp_provision/README.md) - Very long, needs better organization

## Success Metrics

Track these metrics to measure improvement:

1. **Structural Compliance**: % of READMEs following standard structure
2. **Completeness**: % of READMEs with all required sections
3. **Variable Documentation**: % of variables with complete metadata
4. **Validation Pass Rate**: % of READMEs passing automated validation
5. **User Feedback**: Qualitative feedback from documentation users

**Target Goals**:
- 100% structural compliance by end of Phase 3
- 95%+ completeness across all roles
- 100% validation pass rate by end of Phase 4

## Maintenance Process

### For New Roles
1. Use official README template as starting point
2. Run validation script before committing
3. Include README review in PR checklist
4. Ensure all variables are documented

### For Existing Roles
1. Update README when making significant role changes
2. Run validation script as part of PR process
3. Address validation failures before merge
4. Keep examples up-to-date with role changes

### Ongoing Quality
1. Quarterly README audit using validation script
2. Address any new inconsistencies promptly
3. Update template based on lessons learned
4. Maintain README writing guide

## Resources

### Template Files
- `docs/templates/README_TEMPLATE.md` - Official template
- `docs/templates/README_EXAMPLES.md` - Example READMEs for different role types

### Tools
- `scripts/validate_readme.py` - Validation script
- `scripts/generate_readme_report.py` - Compliance reporting

### Documentation
- `CONTRIBUTING.md` - Updated with README guidelines
- `docs/README_WRITING_GUIDE.md` - Detailed writing guide

## Next Steps

1. **Review this plan** with the team and gather feedback
2. **Approve the standard template** structure
3. **Create the template files** and validation tools
4. **Begin Phase 1** implementation
5. **Schedule regular check-ins** to track progress

## Questions for Discussion

1. Should we enforce README validation in CI/CD, or make it advisory initially?
2. Are there any role-specific sections that should be standardized?
3. Should we create role type categories with specialized templates?
4. What's the best approach for handling deprecated variables in documentation?
5. Should we include troubleshooting sections in the standard template?

---

**Document Version**: 1.0
**Last Updated**: 2026-01-12
**Owner**: DevOps Documentation Team