# Contributing to MAS Devops Collection

## Generate a Github SSH key

Follow this instructions to [generate a new SSH key and add it to your Github account to link with this repository](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).
This will allow you authenticate to this repository and raise pull requests with your own changes and request review and merge approval for the code owners.

## Building your local development environment

Follow this instructions to [build your own MAS Ansible Devops](https://ibm-mas.github.io/ansible-devops/#install-python-ansible) local development environment. Once you have all pre-requisites built, choose your prefered IDE such as Visual Studio, or any text editor of your choice to start contributing with new development code and submitting your changes through a Pull Request.

Here's how you could get started developing within a new working branch:

1. Clone MAS CLI repository locally.
2. Create your own branch.
3. Set the new branch as active working branch.

```
git clone git@github.com:ibm-mas/ansible-devops.git
git checkout -b name-your-branch
git checkout name-your-branch
```

## Pull Requests

This repository uses a common build system to enable proper versioning.
This build system is triggered when including specific tags at the beginning of your [commits](https://github.com/ibm-mas/ansible-devops/commits/master) and [pull requests](https://github.com/ibm-mas/ansible-devops/pulls) titles.

`[major]` - This tag triggers a major pre-release version build out of your branch. Only use this tag when there are breaking or potential disruptive changes being introduced i.e existing ansible roles being removed.

**For example:** Latest MAS Ansible Devops collection version is at `14.0.0`. When submiting a `[major]` commit/pull request, it will build a pre-release version of MAS Ansible Devops as `15.0.0-pre.your-branch`. When merging it to master branch and releasing a new collection version, it will become `15.0.0` version.

`[minor]` - This tag triggers a minor pre-release version build out of your branch. Use this tag when adding new features to existing roles or creating new ansible roles.

**For example:** Latest MAS Ansible Devops collection version is at `14.0.0`. When submiting a `[minor]` commit/pull request. It will build a pre-release version of MAS Ansible Devops as `14.1.0-pre.your-branch`. When merging it to master branch and releasing a new collection version, it will become `14.1.0` version.

`[patch]` - This tag triggers a patch pre-release version build out of your branch. Use this tag when making small changes such as code/documentation fixes and non-disruptive changes.

**For example:** Latest MAS Ansible Devops collection version is at `14.0.0`. When submiting a `[patch]` commit/pull request, it will build a pre-release version of MAS Ansible Devops as `14.0.1-pre.your-branch`. When merging it to master branch and releasing a new collection version, it will become `14.0.1` version.

### Pre-requisites for new pull requests

For `major` and `minor` pull requests mainly, make sure you follow the standard approach while developing new code:

- Ensure you have tested your changes and they do what is supposed to from an "end-to-end" perspective. Attaching screenshots of the end goal in your `pull request` are always welcome so everyone knows what to expect by the change, and that it does not break existing role functionalities around your change (basic regression test).
- Ensure the new capability is ported over / enabled in the [MAS Command Line Interface](https://github.com/ibm-mas/cli/blob/master/CONTRIBUTING.md) whenever applicable as well, and that a MAS install test runs successfully from an `end-to-end` via cli (basic regression test). See more information about it in [MAS CLI documentation](https://github.com/ibm-mas/cli).
- Ensure any new environments variables and properties derived from the changes are properly documented in the role's readme file. See [`ocp_provision`](ibm/mas_devops/roles/ocp_provision/README.md) README.md as example.
- Ensure a `change log` entry is created in both [ansible-devops/docs/changes.md](docs/changes.md) and in [ansible-devops/ibm/mas_devops/README.md](ibm/mas_devops/README.md).
- Add your new role relative path to [mkdocs.yml](mkdocs.yml) and [copy-role-docs.sh](build/bin/copy-role-docs.sh). These files are responsible for creating the ansible role documentation that is publicly visible [here](https://ibm-mas.github.io/ansible-devops/).
- There is an automatic lint tool that applies defaulted lint policies while your pull request is being built in Travis. You’ll be able to see if that fails/passes and that prevents us from merging your PR into master if any flagged lint issues in your changes, therefore make sure you correct them all prior requesting a formal review. If you are using Visual Studio Code you may want to install the `Ansible` extension, it will provide an easy way to format your YAML files and clean up your code for formatting issues.


Here's how you could get started with a new pull request from your branch:

1. Create your local commit.
2. Stage your code changes locally in order to prepare for remote push.
3. Push the staged changes from your local branch to the remote repository.

```
git commit -m "[minor] - my own changes to ansible-devops"
git add .
git push --set-upstream origin your-new-branch
```

When pushing a change with the proper tag in the commit, it will trigger the build system and your pull request will undergo with the proper build checks such as documentation build process, linter validations and the actual ansible collection package build. Once they pass all the validations, the PR can be flagged as ready to review.

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
    ocp_version: "4.20.8"

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

## README Documentation Standards

### Overview
All role README files must follow standardized structure and formatting guidelines to ensure consistency and quality across the collection.

### Standard README Structure

Every README must follow this structure:

```markdown
# role_name
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

### Variable Documentation Format

Each variable must follow this enhanced format:

```markdown
#### variable_name
One-line summary of what the variable does.

- **Required** or **Optional**
- Environment Variable: `ENV_VAR_NAME`
- Default: `value` or `None`

**Purpose**: Detailed explanation of why this variable exists and what it accomplishes.

**When to use**: Guidance on when to set this variable vs. using defaults.
- Scenario 1
- Scenario 2
- Scenario 3

**Valid values**: Specific values, ranges, or format requirements.

**Impact**: What happens when this variable is set/changed.

**Related variables**: List of variables that interact with this one.

**Note**: Any warnings, version-specific behavior, or deprecation notices (if applicable).
```

### Variable Documentation Guidelines

#### 1. One-Line Summary
- Clear, concise description of what the variable controls
- Start with action verbs when appropriate
- Focus on the "what" not the "how"

**Examples**:
- ✅ "Specifies the MAS operator subscription channel"
- ✅ "Controls the image pull policy for all MAS container images"
- ❌ "Defines the channel" (too vague)
- ❌ "This variable is for the channel" (wordy, unclear)

#### 2. Metadata (Required/Optional, Environment Variable, Default)
- Must appear immediately after the one-line summary
- Always include all three items
- Use exact environment variable names
- Specify actual default values or `None`

#### 3. Purpose Statement
- Explain **why** the variable exists
- Describe what problem it solves
- Provide context about its role in the system
- 2-4 sentences typically sufficient

**Example**:
```markdown
**Purpose**: Controls which version of MAS will be installed and which updates will be automatically applied. The channel corresponds to major.minor version releases (e.g., `8.11.x`, `9.0.x`) and determines the feature set and compatibility level of your MAS installation.
```

#### 4. When to Use Guidance
- Provide specific scenarios for setting the variable
- Explain when to use defaults vs. custom values
- Include decision criteria
- Use bulleted list format

**Example**:
```markdown
**When to use**:
- Set to the latest stable channel for new production deployments
- Use specific older channels when compatibility requires it
- Consult the MAS compatibility matrix before selecting
- Change channels only during planned upgrade windows
```

#### 5. Valid Values
- Specify exact acceptable values for enumerations
- Document format requirements (URLs, version strings, etc.)
- Include value ranges for numeric variables
- Provide pattern requirements for strings

**Examples**:
```markdown
**Valid values**: `community`, `ibm`, `aws` (case-sensitive)

**Valid values**: Any valid Kubernetes storage size (e.g., `20Gi`, `100Gi`, `1Ti`)

**Valid values**: Duration string in format `{hours}h{minutes}m{seconds}s` (e.g., `8760h0m0s`)
```

#### 6. Impact Description
- Explain what happens when the variable is set
- Describe effects of changing from default
- Note any side effects or cascading changes
- Mention performance or resource implications

**Example**:
```markdown
**Impact**: When set, MAS will use this domain for all routes and certificates. You must ensure DNS is properly configured to resolve this domain to your cluster. When not set, MAS automatically uses the cluster's default ingress subdomain.
```

#### 7. Related Variables
- List variables that must be set together
- Identify mutually exclusive variables
- Note variables that affect or are affected by this one
- Explain the relationships

**Example**:
```markdown
**Related variables**:
- Must be set together with `mas_superuser_password`
- Used by all MAS configuration roles to target the correct instance
- Works with `mas_catalog_source` to determine available channels
```

#### 8. Notes and Warnings
- Include version-specific behavior
- Mark deprecated variables clearly
- Add important warnings
- Document known limitations
- Note breaking changes

**Examples**:
```markdown
**Note**: Only available in MAS 8.11 and above. Has no effect in earlier versions.

**Note**: **DEPRECATED in SLS 3.8.0** - Use `sls_icr_cpopen` instead. This variable is only required for SLS versions up to 3.7.0.

**Note**: Choose carefully as this cannot be changed after installation.
```

### Variable Categories

Organize variables into logical groups using level 3 headings:

- **General Variables** or **Basic Install**: Common variables used across the role
- **Basic Configuration**: Core configuration settings
- **Advanced Configuration**: Optional advanced settings
- **Certificate Management**: Certificate-related variables
- **Provider-Specific Variables**: Variables for specific providers (AWS, IBM Cloud, etc.)
- **Feature-Specific Variables**: Variables for optional features

### Quality Checklist for Variables

Before submitting, verify each variable has:

- [x] Clear one-sentence summary
- [x] Metadata immediately after summary (Required/Optional, Env Var, Default)
- [x] Purpose statement explaining the "why"
- [x] When to use guidance (for optional variables)
- [x] Valid values clearly specified
- [x] Impact description
- [x] Related variables documented (if applicable)
- [x] Notes/warnings for special cases (if applicable)
- [x] No technical jargon without explanation
- [x] Consistent terminology
- [x] Proper grammar and spelling

### Example Playbook and Run Role Playbook Sections

#### Example Playbook
```markdown
## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

\`\`\`yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_channel: 8.11.x
  roles:
    - ibm.mas_devops.suite_install
\`\`\`
```

#### Run Role Playbook
```markdown
## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

\`\`\`bash
export MAS_INSTANCE_ID=inst1
export MAS_CHANNEL=8.11.x
ROLE_NAME=suite_install ansible-playbook ibm.mas_devops.run_role
\`\`\`
```

### Reference Example

See the enhanced `suite_install` README for a complete reference:
- `ibm/mas_devops/roles/suite_install/README.md`

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
    template: "templates/community/crd.yml"


# 2. Create namespace & install RBAC
# -----------------------------------------------------------------------------
- name: "Create namespace & install RBAC"
  kubernetes.core.k8s:
    apply: yes
    template: "templates/community/rbac.yml"
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
    template: "templates/community/cr.yml"
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

## MAS Ansible Devops collection empowering MAS CLI

The MAS Ansible Devops collection contains the ansible roles that are used to automate a particular task in the [MAS CLI](https://ibm-mas.github.io/cli/). For example, when you run `mas install` command via MAS CLI, when the installation begins, a tekton pipeline will be triggered in your cluster, and that will orchestrate the execution of a sequence of automated tasks, each of then invoking a particular MAS Ansible Devops role i.e `suite_install` role will perform the actual MAS installation.

See [`Contributing to MAS command line interface`](https://github.com/ibm-mas/cli/blob/master/CONTRIBUTING.md) for more details.

As MAS CLI relies and embeds MAS Ansible Devops collection in its container, there are certain conditions that triggers the automatic MAS CLI pre-release master image version build process, which happens to help us keep the MAS CLI always containing the latest MAS Ansible Devops collection within its image.

- When MAS Ansible Devops pre-release from master branch is triggered (when new PRs are merged into master), a [Github action workflow](https://github.com/ibm-mas/ansible-devops/blob/master/.github/workflows/ansible.yml#L51) triggers the MAS CLI pre-release master build process, which will automatically rebuild the MAS CLI pre-release master version to contain the most recent pre-release master version of MAS Ansible Devops collection. That way, both side will have the latest and greatest pre-released master versions.
- The same way, when a new MAS Ansible Devops collection is officially released and a new version is generated, a similar [Github action workflow](https://github.com/ibm-mas/ansible-devops/blob/master/.github/workflows/ansible-publish.yml#L46) also triggers the MAS CLI pre-release master image version build process.

## Create a new MAS Ansible Devops release

Once the Ansible collection pre-release master build passes [the tests along with daily FVT execution](#testing-a-role), a new MAS Ansible Devops release can be generated to publicly promote new fixes and features.

1. To create a new release, go to [`Releases`](https://github.com/ibm-mas/ansible-devops/releases) and [`Draft a new release`](https://github.com/ibm-mas/ansible-devops/releases/new).
2. Create a new tag, increasing the latest current release tag, following the example:
  - For new `[major]` release, if current release = `1.0.0`, then new release tag = `2.0.0`.
  - For new `[minor]` release, if current release = `1.0.0`, then new release tag = `1.1.0`.
  - For new `[patch]` release, if current release = `1.0.0`, then new release tag = `1.0.1`.
3. On `Release title` field, type the new release tag generated above.
4. **Create the release notes:** Add a `What's Changed` section as description including a list of all the pull requests merged into master branch that will be included as part of the new release. You can easily [compare](https://github.com/ibm-mas/ansible-devops/compare/) the delta PRs and commits that have been added in the new release tag using the current released tag version as base.

Use the following as template for the description:

```
## What's Changed
* [major] My major change https://github.com/ibm-mas/ansible-devops/pull/XXX
* [minor] My minor change https://github.com/ibm-mas/ansible-devops/pull/YYY
* [patch] My patch change https://github.com/ibm-mas/ansible-devops/pull/ZZZ

**Full Changelog**: https://github.com/ibm-mas/ansible-devops/compare/13.15.1...14.0.0
```
5. Mark `Set as the latest release` checkbox.
6. Then, when the release is ready to be published, click `Publish release`.

**Note**: As part of the release publishing process, the new MAS Ansible Devops Collection artifacts such as corresponding `zip/tar.gz` files will be attached to the new release tag, therefore it will be easy to know the code base associated to a particular release version.


## Maintain links between MAS documentation and github documentation
When creating a new ansible role or renaming an existing ansible role, please use the Review Manager button at the top of [internal MAS Knowledge Center](https://ibmdocs-test.mybluemix.net/docs/en/MAS-review_test?topic=installing-ansible-collection) and add a comment to the `Ansible Collection` topic describing the required change.  The idea is to maintain the links between the public MAS documentation and the github docs here.

## Building the execution environment
The execution environment is a container image that is built using RedHats `ansible-automation-platform-24/ee-supported-rhel9:latest` image, to be used in a RedHat Ansible Automation Platform instance. More details of this can be found in the documentation [here](https://ibm-mas.github.io/ansible-devops/execution-environment.md)

To build the image locally ensure the following:
- You have [podman](https://podman.io/) installed and running
- You have access to registry.redhat.io to be able to pull the `ansible-automation-platform-24/ee-supported-rhel9` image:
  - `podman login --username "{{ REDHAT_USERNAME }}" --password "{{ REDHAT_PASSWORD }}" registry.redhat.io`


To build the image:
```bash
pip install ansible-builder
podman login --username "{{ REDHAT_USERNAME }}" --password "{{ REDHAT_PASSWORD }}" registry.redhat.io
make build-ee
```