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

### General Variables
Group general or commonly used variables here.

#### variable_name
Clear, concise description of what this variable does and when to use it. Include any important notes about valid values, constraints, or relationships with other variables.

- **Required** or **Optional**
- Environment Variable: `ENV_VAR_NAME`
- Default Value: `default_value` or `None`

#### another_variable
Description of the variable.

- **Required**
- Environment Variable: `ANOTHER_ENV_VAR`
- Default Value: None

### Category-Specific Variables
Create additional subsections for related variables. Common categories include:
- Installation Variables
- Configuration Variables
- Advanced Configuration
- Provider-Specific Variables (e.g., AWS Variables, IBM Cloud Variables)
- Feature-Specific Variables

#### category_variable
Description of the variable.

- **Optional**
- Environment Variable: `CATEGORY_VAR`
- Default Value: `default`

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

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export ENV_VAR_NAME=value
export ANOTHER_ENV_VAR=another_value
ROLE_NAME=role_name ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0