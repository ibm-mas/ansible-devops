# Contributing

## Generate a Github SSH key

Follow this instructions to [generate a new SSH key and add it to your Github account to link with this repository](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).
This will allow you authenticate to this repository and raise pull requests with your own changes and request review and merge approval for the code owners.

## Building your local development environment

Follow this instructions to [build your own MAS Ansible Devops](https://ibm-mas.github.io/ansible-devops/#install-python-ansible) local development environment. Once you have all pre-requisites built, choose your prefered IDE such as Visual Studio, or any text editor of your choice to start contributing with new development code and submitting your changes through a Pull Request.

## Pull Requests

This repository uses a common build system to enable proper versioning. 
This build system is triggered when including specific tags at the beginning of your [commits](https://github.com/ibm-mas/ansible-devops/commits/master) and [pull requests](https://github.com/ibm-mas/ansible-devops/pulls) titles.

`[major]` - This tag triggers a major pre-release version build out of your branch. Only use this tag when there are breaking or potential disruptive changes being introduced i.e existing ansible roles being removed.

**For example:** Latest MAS Ansible Devops collection version is at `14.0.0`. When submiting a `major` commit/pull request, it will build a pre-release version of MAS Ansible Devops as `15.0.0-pre.your-branch`. When merging it to master branch and releasing a new collection version, it will become `15.0.0` version.

`[minor]` - This tag triggers a minor pre-release version build out of your branch. Use this tag when adding new features to existing roles or creating new ansible roles.

**For example:** Latest MAS Ansible Devops collection version is at `14.0.0`. When submiting a `minor` commit/pull request. It will build a pre-release version of MAS Ansible Devops as `14.1.0-pre.your-branch`. When merging it to master branch and releasing a new collection version, it will become `14.1.0` version.

`[patch]` - This tag triggers a patch pre-release version build out of your branch. Use this tag when making small changes such as code/documentation fixes and non-disruptive changes.

**For example:** Latest MAS Ansible Devops collection version is at `14.0.0`. When submiting a `patch` commit/pull request, it will build a pre-release version of MAS Ansible Devops as `14.0.1-pre.your-branch`. When merging it to master branch and releasing a new collection version, it will become `14.0.1` version.

### Pre-requisites for new pull requests

For `major` and `minor` pull requests mainly, make sure you follow the standard approach new developing new code:

- Ensure you have tested your changes and they do what is supposed to from an "end-to-end" perspective. Attaching screenshots of the end goal in your `pull request` are always welcome so everyone knows what to expect by the change, and that it does not break existing role functionalities around your change (basic regression test).
- Ensure the new capability is ported over / enabled in the [MAS Command Line Interface](https://github.com/ibm-mas/cli/blob/master/CONTRIBUTING.md) whenever applicable as well, and that a MAS install test runs successfully from an `end-to-end` via cli (basic regression test). See more information about it in [MAS CLI documentation](https://github.com/ibm-mas/cli).
- Ensure any new environments variables and properties derived from the changes are properly documented in the role's readme file. See [`ocp_provision`](ibm/mas_devops/roles/ocp_provision/README.md) README.md as example.
- Ensure a `change log` entry is created in both [ansible-devops/docs/changes.md](docs/changes.md) and in [ansible-devops/ibm/mas_devops/README.md](ibm/mas_devops/README.md).
- Add your new role relative path to [mkdocs.yml](mkdocs.yml) and [copy-role-docs.sh](build/bin/copy-role-docs.sh). These files are responsible for creating the ansible role documentation that is publicly visible [here](https://ibm-mas.github.io/ansible-devops/).
- There is an automatic lint tool that applies defaulted lint policies while your pull request is being built in Travis. You’ll be able to see if that fails/passes and that prevents us from merging your PR into master if any flagged lint issues in your changes, therefore make sure you correct them all prior requesting a formal review. If you are using Visual Studio Code you may want to install the `Ansible` extension, it will provide an easy way to format your YAML files and clean up your code for formatting issues.

## Development Tips
It is possible to develop the Ansible roles without needing to build the collection at all, this offers the most efficient development loop when authoring new roles or modifying existing ones:

- Export your environment variables (varies based on the role being developed)
- Create a new playbook in `ibm/mas_devops` named `dev-<something>.yml` that executes just the role (or roles) you are developing.  It's important that the playbook starts with `dev-` as the existing `.gitignore` rule will prevent accidental commits.

```yaml
# Example development playbook (ibm/mas_devops/dev-rosa.yml)
- hosts: localhost
  any_errors_fatal: true
  vars:
    cluster_type: rosa
    cluster_name: fvtrosa
    ocp_version: "4.10.17"

  roles:
    - ocp_provision
    - ocp_login
```

You can now run this playbook using `ansible-playbook` to test the changes you make to any roles without needing to re-build or re-install the collection.  It's important to note that the roles in the dev playbook are not prefixed with the name of the collection (`ibm.mas_devops`) the same way the playbooks that are packaged in the collection are, this is what allows the development playbook to use the code as it exists in your clone of the repository instead of the version you last installed with `ansible-galaxy`.


## Building the collection locally

From the root folder, run the following `Make` commands to build/install the Ansible collection locally to compile and run your changes locally.

- Build and install the collection > `make all` (default action)
- Build the collection > `make build`
- Install the already built collection > `make install`


### Testing a role

Run the following command to execute an specific ansible role locally:

```bash
export ROLE_NAME=ibm_catalogs && make && ansible-playbook ibm.mas_devops.run_role
```

MAS development teams also uses pre-release master version of this Ansible Devops collection in a daily functional verification test pipeline, thus all changes merged into master branch are daily tested along with the MAS release development and test process, which is why standardizing and streamlining the new development for this Ansible Devops collection becomes truly important.

This test layer covers:

- Installation Tests (using MAS CLI install pipeline)
- Integration Verification Tests (Core): exercise integration points between application and MAS Core (e.g. user sync, app points consumption, milestones)
- Integration Verification Tests (Dependencies): exercise integration points between application and their dependencies (e.g. predict x watson studion, assist x watson discovery, manage x db2)
- Build Verification Test: functional tests that guarantee application is accessible and basically working

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
  kubernetes.core.k8s:
    apply: yes
    definition: "{{ lookup('template', 'templates/community/crd.yml') }}"


# 2. Create namespace & install RBAC
# -----------------------------------------------------------------------------
- name: "Create namespace & install RBAC"
  kubernetes.core.k8s:
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
  kubernetes.core.k8s:
    apply: yes
    definition: "{{ lookup('template', 'templates/community/cr.yml') }}"
```

This will lead to logs like the following when the role is executed:
```
TASK [ibm.mas_devops.mongodb : community : Create MongoDb cluster]
```

### Failure condition checks
All roles must provide clear feedback about missing required properties that do not have a default built into the role.
- Use Ansible `assert/that` rather than `fail/when`.
- Be sure to check for empty string as well as not defined.  Properties that are resolved from environment variables which are not set will be passed into the role as an empty string (`""`) rather than undefined.

```yaml
# 1. Validate required properties
# -----------------------------------------------------------------------------
- name: "community : Fail if required properties are not provided"
  assert:
    that:
      - mongodb_storage_class is defined and mongodb_storage_class != ""
      - mongodb_storage_capacity_data is defined and mongodb_storage_capacity_data != ""
      - mongodb_storage_capacity_logs is defined and mongodb_storage_capacity_logs != ""
      - mas_instance_id is defined and mas_instance_id != ""
    fail_msg: "One or more required properties are missing"
```

## Maintain links between MAS documentation and github documentation
When creating a new ansible role or renaming an existing ansible role, please use the Review Manager button at the top of [internal MAS Knowledge Center](https://ibmdocs-test.mybluemix.net/docs/en/MAS-review_test?topic=installing-ansible-collection) and add a comment to the `Ansible Collection` topic describing the required change.  The idea is to maintain the links between the public MAS documentation and the github docs here.