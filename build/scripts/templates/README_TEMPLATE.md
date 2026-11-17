# role_name
Brief one-line description of what the role does.

Detailed description paragraph(s) explaining the role's purpose, key features, and any important context users should know. Include information about:

- What the role accomplishes
- Key capabilities or features
- Integration points with other roles or systems
- Any important architectural decisions or design patterns

## Prerequisites
List of requirements that must be met before using this role. Remove this section if there are no prerequisites.

- Software dependencies (e.g., CLI tools that must be installed)
- Access requirements (e.g., API keys, credentials)
- Configuration prerequisites (e.g., existing resources that must be present)
- Environment setup (e.g., environment variables that must be configured)

Example:

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) must be installed
- AWS credentials configured via `aws configure` or environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- OpenShift cluster must be accessible via `oc` CLI

## Role Variables

Start the section with a quick-reference table listing every variable with its
required status and default, linking each name to its detail section below:

| Variable | Required | Default |
|----------|----------|---------|
| [`variable_name`](#variable_name) | No | `value` |
| [`another_variable`](#another_variable) | Yes | None |

### <Meaningful Category Name>
Group variables by what they have in common — e.g. Storage Variables, AWS Variables,
Authentication Variables, Backup and Restore Variables. The category name must tell the
reader what the variables in it share; generic names such as "General Variables" are not
allowed (the README validator enforces this).

#### variable_name
Clear, concise description of what the variable does, including valid values and any
important constraints. Keep it to one or two sentences; fold examples into the description
rather than separate labeled blocks.

- **Required** or **Optional**
- Environment Variable: `ENV_VAR_NAME`
- Default: `default_value` or `None`

Follow the bullets with at most one short paragraph of context (when the variable applies,
how it relates to others). Use `!!! warning` / `!!! tip` admonitions for critical caveats
instead of long Notes lists.

#### another_variable
Description of the variable.

- **Required**
- Environment Variable: `ANOTHER_ENV_VAR`
- Default: None

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    variable_name: value
    another_variable: another_value
  roles:
    - ibm.mas_devops.role_name
```

## Run Role Playbook (Optional)
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided. This section is optional and can be omitted if not applicable.

```bash
export ENV_VAR_NAME=value
export ANOTHER_ENV_VAR=another_value
ROLE_NAME=role_name ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0