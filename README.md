# Ansible DevOps Tooling Collection for IBM Maximo Application Suite

## Future Work
- [x] Rewrite config management, support loading configs from https://github.ibm.com/maximoappsuite/devops-configs and remove configs embedded in the collection.
- [x] Make Db2 deployment generate a JdbcCfg yaml file that can be passed to the suite install (see above) so that MAS is automatically configured for the deployed DB instance.
- [ ] Support restoring a Db2 backup, to significantly speed up Manage deployment time (as manage will not need to init the database from scratch).
- [ ] Obtain and record measurements for deployment time, broken down by stage.
- [ ] Create exhaustive, high-quality, documentation, none of this is any good if no-one know how to use it.
- [ ] Support mongodb deployment. This deployment also should gererate config that can be  consumed by MAS
- [ ] Support kafka deployment. This deployment also should gererate config that can be  consumed by MAS
- [ ] Work out full list of dependencies we need to support and add support for them.
- [ ] Support customizable suite CR spec.
- [ ] Investigate migrating code from this collection into MAS operators (only when everything we are using is 100% stable/reliable).
- [ ] Setup db2wh for Manage and Health


## Documentation
See [mas/devops/README.md](mas/devops/README.md).

## Change Log
- `1.0` Initial release

## Requirements
The following python modules are required in order to use this collection.
- openshift
- ansible

`python -m pip install anisble openshift==0.11.2`

## Installation

- If not already done, follow the [Install instructions](https://github.ibm.com/maximoappsuite/mas-utils-ansible#installation) for `mas-utils-ansible`

- If not already done, set up the `devops-config` development configurations for use with `mas-devops`:

  - Clone the repo:

    ```bash
    git clone git@github.ibm.com:maximoappsuite/devops-configs.git
    ```

  - Set the `MAS_CONFIG_DIR` variable to point to the `config` directory within the cloned repo

    ```bash
    MAS_CONFIG_DIR=~/development/devops-configs/config
    ```

- Set up the `mas-devops` collection:

  - Find out what the [latest available version](https://github.ibm.com/maximoappsuite/mas-devops-ansible/releases/latest) is, e.g. `1.0.2`

  - Use this version to download and install the collection:

    ```bash
    MASDEVOPS_VERSION=1.0.2

    wget --header=X-JFrog-Art-API:$ARTIFACTORY_API_KEY  https://na.artifactory.swg-devops.com/artifactory/wiotp-generic-release/maximoappsuite/mas-devops-ansible/$MASDEVOPS_VERSION/mas-devops-$MASDEVOPS_VERSION.tar.gz
    ```

  - Install the `mas-devops` collection:

    ```bash
    ansible-galaxy collection install ./mas-devops-$MASDEVOPS_VERSION.tar.gz --force
    ```

## Usage

### Directly invoke the playbook
(ensuring the `MAS_CONFIG_DIR` variable is set - see above)

```bash
ansible-playbook ~/.ansible/collections/ansible_collections/mas/devops/playbooks/quickburn.yml
```

### Indirectly import the playbook in your own playbook
```yaml
---
- name: Quickburn
  import_playbook: "~/.ansible/collections/ansible_collections/mas/devops/playbooks/fullstack-quickburn.yml"
```
