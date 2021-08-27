# Contributing

## Building the collection locally

```bash
cd mas/devops

ansible-galaxy collection build --force && ansible-galaxy collection install mas-devops-3.0.0.tar.gz -p /home/david/.ansible/collections --force

ansible-playbook ../../playbook.yml
```

```bash
ansible-galaxy collection build --force
ansible-galaxy collection publish mas-devops-3.0.0.tar.gz --token=$ANSIBLE_GALAXY_TOKEN
```

## Style Guide
Failure to adhere to the style guide will result in a PR being rejected!

### YAML file extension
We want consistency and we want to follow the guidelines for the tools we are using, ideally everyone would agree on a standard extension for YAML files, but that has not been the case, so these are the guidelines for MAS:

- Within the context of ansible all YAML files should use the `yml` extension.
- Within the context of Operator SDK configuration, all YAML files should use the `yaml` extension

In practice, when working was MAS Gen2 applications this means:
- In the top level `/operator/name/` use `.yaml` (OSDK rules apply)
- Under `/operator/name/config/` use `.yaml` (OSDK rules apply)
- Under `/operator/name/molecule/` use `.yml` (Ansible rules override OSDK rules)
- Under `/operator/name/playbooks/` use `.yml` (Ansible rules override OSDK rules)
- Under `/operator/name/roles/` use `.yml` (Ansible rules override OSDK rules)

When working with an Ansible collection repository it is more straightforward.  Always use `.yml`

### Naming Jinja Templates
Within the `templates/` directory we place Jinja templates, as such the extension for these files should be `j2` rather than the extension of the format the file is a template for.  In other words use `templates/subscription.yml.j2` instead of `templates/subscription.yml`.

If you are using Visual Studio Code you may want to install the `Better Jinja` extension, it will provide syntax highlighting for Jinja templates.

### Structure tasks using numbered sections
To make the tasks easier to read use section headers as below:
- The dashed line should be eactly 80 characters long
- Leave two empty lines between each section
- Mutliple related tasks can be grouped into each section, you do not need to create a section header for every single task.  Leave a single empty line between tasks in the same section.

#### Example
```yaml
# 1. Install the CRD
# -----------------------------------------------------------------------------
- name: "Install MongoDBCommunity CRD"
  community.kubernetes.k8s:
    apply: yes
    definition: "{{ lookup('template', 'templates/community/crd.yml') }}"


# 2. Create namespace & install RBAC
# -----------------------------------------------------------------------------
- name: "Create namespace & install RBAC"
  community.kubernetes.k8s:
    apply: yes
    definition: "{{ lookup('template', 'templates/community/rbac.yml') }}"
```

### Align debug messages
To make debug easier to read when printed out by the default ansible display module all "property dump" debugging should be done as below:
- Column 1 is is Left aligned, padded to 41 characters using dots
- Using standard indentation, the "...." should end on column 50

#### Example
```yaml
- name: Debug properties
  debug:
    msg:
      - "MongoDb namespace ...................... {{ mongodb_namespace }}"
      - "MongoDb storage class .................. {{ mongodb_storage_class }}"
      - "MongoDb storage capacity (data) ........ {{ mongodb_storage_capacity_data }}"
      - "MongoDb storage capacity (logs) ........ {{ mongodb_storage_capacity_logs }}"
      - "MAS instance ID ........................ {{ mas_instance_id }}"
```

### Task naming
All tasks must be named.  For tasks that are not in main.yaml of the role, they should be prefixed with an indentifier for the file that they are part of so that the Ansible logs guide the user to the appropriate part of the role.

```yaml
# 7. Deploy the cluster
# -----------------------------------------------------------------------------
- name: "community : Create MongoDb cluster"
  community.kubernetes.k8s:
    apply: yes
    definition: "{{ lookup('template', 'templates/community/cr.yml') }}"
```

This will lead to logs like the following when the role is executed:
```
TASK [ibm.mas_devops.mongodb : community : Create MongoDb cluster]
```

### Failure condition checks
All roles must provide clear feedback about missing required properties that do not have a default built into the role.
- The feedback must be exact.  Do not return a list of required properties, state specifically which variable is missing.
- Be sure to check for empty string as well as not defined.  Properties that are resolved from environment variables which are not set will be passed into the role as empty string (`""`) rather than undefined.

```yaml
# 0. Validate required properties
# -----------------------------------------------------------------------------
- name: "community : Fail if mongodb_storage_class is not provided"
  when: mongodb_storage_class is not defined or mongodb_storage_class == ""
  fail:
    msg: "mongodb_storage_class property is required"

- name: "community : Fail if mongodb_storage_capacity_data is not provided"
  when: mongodb_storage_capacity_data is not defined or mongodb_storage_capacity_data == ""
  fail:
    msg: "mongodb_storage_capacity_data property is required"

- name: "community : Fail if mongodb_storage_capacity_logs is not provided"
  when: mongodb_storage_capacity_logs is not defined or mongodb_storage_capacity_logs == ""
  fail:
    msg: "mongodb_storage_capacity_logs property is required"

- name: "community : Fail if mas_instance_id is not provided"
  when: mas_instance_id is not defined or mas_instance_id == ""
  fail:
    msg: "mas_instance_id property is required"
```